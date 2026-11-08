import os
from src.config import Config
from src.image_client import ImageClientFactory
from src.llm_client import ClientFactory
from src.languages import get_language, list_languages

from src.agents.feasibility    import FeasibilityAgent
from src.agents.planner        import ScenePlanner
from src.agents.scene_director import SceneDirector

from src.tools.merger       import VideoMerger
from src.tools.manim_runner import render_code_string
from src.tools.cleanup      import cleanup
from src.templates.registry import get_template, get_template_requirements


def run_pipeline(
    topic: str,
    lang_code: str = "en",
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    clean_up: bool = True,
    api_base: str | None = None,
    want_image: bool = False,
    image_provider: str | None = None,
    image_model: str | None = None,
    image_api_key: str | None = None,
) -> str | None:
    image_client = (
        ImageClientFactory.create(image_provider, image_model, image_api_key)
        if want_image
        else None
    )
    enabled_capabilities = {"image_generation"} if image_client else set()

    lang_cfg = get_language(lang_code)
    print(f"🚀 Starting Imagio Pipeline: {topic}")
    print(f"🌐 Language: {lang_cfg['name']}  |  TTS: {lang_cfg['piper_model']}")

    # Build agent configuration (single provider & model for all agents if specified)
    agent_config = {
        "provider": provider or Config.DEFAULT_PROVIDER,
        "model": model or Config.DEFAULT_MODEL,
        "api_key": api_key,
        "api_base": api_base,
    }
    print(f"🤖 LLM Provider: {agent_config['provider']}  |  Model: {agent_config['model']}")

    feasibility_agent = FeasibilityAgent(ClientFactory.get_client(agent_config))
    planner_agent     = ScenePlanner(ClientFactory.get_client(agent_config))
    director_agent    = SceneDirector(ClientFactory.get_client(agent_config))
    merger_tool       = VideoMerger()

    # ── Step 1: Feasibility ───────────────────────────────────────
    print("\n📝 Step 1: Feasibility Analysis...")
    analysis = feasibility_agent.analyze_topic(topic, lang_code=lang_code)
    if not analysis.get("feasible"):
        print(f"❌ Rejected: {analysis.get('reason')}")
        return None

    curriculum = analysis.get("curriculum")
    if not curriculum:
        print("❌ No curriculum returned")
        return None
    print(f"✅ Approved: {curriculum.get('title')}")

    # ── Step 2: Planning ──────────────────────────────────────────
    print("\n🧠 Step 2: Planning Scenes...")
    scene_plans = planner_agent.plan_scenes(
        curriculum,
        lang_code=lang_code,
        enabled_capabilities=enabled_capabilities,
    )
    print(f"  ✓ {len(scene_plans)} scenes planned")

    # ── Step 3: Production Loop ───────────────────────────────────
    final_videos = []
    prev_script  = ""

    print("\n⚙️  Step 3: Production Loop")
    for i, plan in enumerate(scene_plans, 1):
        scene_id      = f"scene_{i:02d}"
        template_name = plan.get("template_type") or plan.get("template", "bullet_points")
        concept       = plan.get("concept", "Untitled")

        print(f"\n  🎬 {scene_id}: {concept} [{template_name}]")

        try:
            tmpl = get_template(template_name)
        except KeyError:
            print(f"  ⚠️  Unknown template '{template_name}' → bullet_points")
            tmpl          = get_template("bullet_points")
            template_name = "bullet_points"

        tmpl.set_language(lang_code)

        # Pre-load Manim class docs the Planner declared for this scene.
        relevant_classes = plan.get("relevant_classes") or []
        preloaded_docs   = ""
        if relevant_classes:
            blocks = []
            for class_name in relevant_classes:
                if not isinstance(class_name, str):
                    continue  # Planner hallucinated a non-string; skip silently.
                doc_path = os.path.join("source", "classes", f"{class_name}.txt")
                if os.path.exists(doc_path):
                    with open(doc_path, "r", encoding="utf-8") as f:
                        blocks.append(f"### {class_name}\n{f.read()}")
                else:
                    print(f"  ⚠️  Class not found: {class_name}")
            if blocks:
                preloaded_docs = "\n\n".join(blocks)

        print("  ✍️  Directing scene...")
        direction = director_agent.direct_scene(
            template_name   = template_name,
            schema          = tmpl.schema(),
            template_hint   = tmpl.prompt(),
            concept         = concept,
            previous_script = prev_script,
            lang_code       = lang_code,
            choreography    = plan.get("choreography"),
            preloaded_docs  = preloaded_docs,
        )

        script        = direction.get("script", "")
        template_data = direction.get("template_data", {})
        prev_script   = script

        if "image_generation" in get_template_requirements(template_name):
            if image_client is None:
                raise RuntimeError(
                    f"Template '{template_name}' requires image generation, "
                    "but image generation is not enabled."
                )
            image_prompt = template_data.get("image_prompt")
            if not isinstance(image_prompt, str) or not image_prompt.strip():
                raise ValueError(
                    f"Template '{template_name}' requires a non-empty image_prompt."
                )
            template_data["image_path"] = image_client.generate_image(image_prompt)

        print("  👨‍💻 Generating Manim code...")
        scene_code = tmpl.code(template_data, script)

        os.makedirs("workspace/code", exist_ok=True)
        code_path = f"workspace/code/{scene_id}.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(scene_code)

        print(f"  🎥 Rendering ({lang_cfg['name']}, {lang_cfg['piper_model']})...")
        result = render_code_string(
            code        = scene_code,
            scene_name  = scene_id,
            code_dir    = "workspace/code",
            output_dir  = "workspace/media",
            max_retries = 3,
        )

        if not result.success:
            print(f"  ❌ Render failed — skipping")
            continue

        print(f"  ✅ {result.mp4_path}")
        final_videos.append(result.mp4_path)

    # ── Step 4: Assembly ──────────────────────────────────────────
    if not final_videos:
        print("\n❌ No scenes rendered successfully")
        return None

    print(f"\n🎞️  Step 4: Assembling {len(final_videos)} scenes...")
    final = merger_tool.merge_all_scenes(
        final_videos,
        output_filename=f"final_{lang_code}.mp4",
    )
    print(f"\n✨ Done! → {final}")

    # if clean_up:
    #     print(f"\n🧹 Step 5: Cleanup...")
    #     cleanup(
    #         workspace_dir    = "workspace",
    #         remove_code      = True,
    #         remove_partials  = True,
    #         remove_scenes    = False,   # ← NEVER delete the final video here.
    #         remove_tts_cache = True,    #   server.py reads it into memory then
    #         verbose          = True,    #   deletes it itself after streaming.
    #     )

    # server.py reads this file into memory, then deletes it.
    return final