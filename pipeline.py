import os
from src.config import Config
from src.llm_client import ClientFactory
from src.languages import get_language, list_languages

from src.agents.feasibility    import FeasibilityAgent
from src.agents.planner        import ScenePlanner
from src.agents.scene_director import SceneDirector

from src.tools.merger       import VideoMerger
from src.tools.manim_runner import render_code_string
from src.tools.cleanup      import cleanup
from src.templates.registry import get_template


def run_pipeline(topic: str, lang_code: str = "en", clean_up: bool = True) -> str | None:
    lang_cfg = get_language(lang_code)
    print(f"🚀 Starting Imagio Pipeline: {topic}")
    print(f"🌐 Language: {lang_cfg['name']}  |  TTS: {lang_cfg['piper_model']}")

    feasibility_agent = FeasibilityAgent(ClientFactory.get_client(Config.FEASIBILITY_CONFIG))
    planner_agent     = ScenePlanner(ClientFactory.get_client(Config.PLANNER_CONFIG))
    director_agent    = SceneDirector(ClientFactory.get_client(Config.DIRECTOR_CONFIG))
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
    scene_plans = planner_agent.plan_scenes(curriculum, lang_code=lang_code)
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

        print("  ✍️  Directing scene...")
        direction = director_agent.direct_scene(
            template_name   = template_name,
            schema          = tmpl.schema(),
            concept         = concept,
            previous_script = prev_script,
            lang_code       = lang_code,
        )

        script        = direction.get("script", "")
        template_data = direction.get("template_data", {})
        prev_script   = script

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


if __name__ == "__main__":
    run_pipeline("The Geometry of Linear Algebra", lang_code="en")