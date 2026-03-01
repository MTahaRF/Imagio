# pipeline.py
import os
from src.config import Config
from src.llm_client import ClientFactory

from src.agents.feasibility    import FeasibilityAgent
from src.agents.planner        import ScenePlanner
from src.agents.scene_director import SceneDirector  

from src.tools.merger       import VideoMerger
from src.tools.manim_runner import render_code_string
from src.templates.registry import get_template

def run_pipeline(topic: str):
    print(f"🚀 Starting Imagio Pipeline: {topic}")

    # ── Init ──────────────────────────────────────────────────────
    feasibility_agent = FeasibilityAgent(ClientFactory.get_client(Config.FEASIBILITY_CONFIG))
    planner_agent     = ScenePlanner(ClientFactory.get_client(Config.PLANNER_CONFIG))
    director_agent    = SceneDirector(ClientFactory.get_client(Config.DIRECTOR_CONFIG))
    merger_tool       = VideoMerger()

    # ── Step 1: Feasibility ───────────────────────────────────────
    print("\n📝 Step 1: Feasibility Analysis...")
    analysis = feasibility_agent.analyze_topic(topic)
    if not analysis.get("feasible"):
        print(f"❌ Rejected: {analysis.get('reason')}")
        return

    curriculum = analysis.get("curriculum")
    if not curriculum:
        print("❌ No curriculum returned")
        return
    print(f"✅ Approved: {curriculum.get('title')}")

    # ── Step 2: Planning ──────────────────────────────────────────
    print("\n🧠 Step 2: Planning Scenes...")
    scene_plans = planner_agent.plan_scenes(curriculum)
    print(f"  ✓ {len(scene_plans)} scenes planned")

    # ── Step 3: Production Loop ───────────────────────────────────
    final_videos    = []
    prev_script     = ""

    print("\n⚙️  Step 3: Production Loop")
    for i, plan in enumerate(scene_plans, 1):
        scene_id      = f"scene_{i}"
        template_name = plan.get("template_type") or plan.get("template", "bullet_points")
        concept       = plan.get("concept", "Untitled")

        print(f"\n  🎬 {scene_id}: {concept} [{template_name}]")

        # ── Resolve template ──────────────────────────────────────
        try:
            tmpl = get_template(template_name)
        except KeyError:
            print(f"  ⚠️ Unknown template '{template_name}' → fallback bullet_points")
            tmpl = get_template("bullet_points")
            template_name = "bullet_points"

        # ── SceneDirector: co-write script + data ─────────────────
        print("  ✍️  Directing scene...")
        direction = director_agent.direct_scene(
            template_name=template_name,
            schema=tmpl.schema(),
            concept=concept,
            previous_script=prev_script
        )

        script        = direction.get("script", "")
        template_data = direction.get("template_data", {})
        prev_script   = script

        # ── Generate Manim code with voiceover baked in ───────────
        print("  👨‍💻 Generating Manim code...")
        scene_code = tmpl.code(template_data, script)

        os.makedirs("workspace/code", exist_ok=True)
        code_path = f"workspace/code/{scene_id}.py"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(scene_code)

        # ── Render ────────────────────────────────────────────────
        print("  🎥 Rendering (audio baked in via Kokoro)...")
        result = render_code_string(
            code=scene_code,
            scene_name=scene_id,
            code_dir="workspace/code",
            output_dir="workspace/media",
            max_retries=3,
        )

        if not result.success:
            print(f"  ❌ Render failed — skipping scene")
            continue

        print(f"  ✅ {result.mp4_path}")
        final_videos.append(result.mp4_path)

    # ── Step 4: Final Assembly ────────────────────────────────────
    if not final_videos:
        print("\n❌ No scenes rendered — pipeline failed")
        return

    print(f"\n🎞️  Step 4: Assembling {len(final_videos)} scenes...")
    final = merger_tool.merge_all_scenes(final_videos)
    print(f"\n✨ Done! → {final}")

if __name__ == "__main__":
    run_pipeline("The Geometry of Linear Algebra")
