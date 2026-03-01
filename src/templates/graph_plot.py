from .base import BaseTemplate

class GraphPlotTemplate(BaseTemplate):

    def description(self) -> str:
        return (
            "Use when a scene needs to plot a mathematical function on a 2D coordinate "
            "system. Best for calculus, physics, and signal-related topics. "
            "Do NOT use for pure text, equations without graphs, or comparisons."
        )

    def schema(self) -> dict:
        return {
            "title":    "Heading above the graph",
            "function": "Python expression using x and np (e.g. 'np.sin(2 * x)')",
            "x_min": "-4", "x_max": "4",
            "y_min": "-2", "y_max": "2",
            "x_label": "x", "y_label": "y",
            "color":   "BLUE",
            "caption": "Short plain-text description shown below the graph",
            "narrations": {
                "axes":    "Spoken narration when the axes appear",
                "graph":   "Spoken narration when the curve is drawn",
                "caption": "Spoken narration for the caption (or empty string)",
            },
        }

    def prompt(self) -> str:
        return (
            "You are filling JSON for a Manim function-graph scene.\n"
            "Return ONLY a JSON object — no markdown, no explanation.\n\n"
            "Schema:\n"
            "{\n"
            '  "title": "Graph heading", "function": "np.sin(2 * x)",\n'
            '  "x_min": "-4", "x_max": "4", "y_min": "-2", "y_max": "2",\n'
            '  "x_label": "x", "y_label": "y", "color": "BLUE",\n'
            '  "caption": "Short description",\n'
            '  "narrations": {"axes": "Axes narration", "graph": "Graph narration", "caption": "Caption narration"}\n'
            "}\n\n"
            "Rules:\n"
            "- function must be a valid Python expression using x and np.\n"
            "- color must be one of: BLUE, GREEN, YELLOW, RED, ORANGE, PURPLE, TEAL, WHITE.\n"
            "- Each narration is a natural spoken sentence (max 25 words).\n"
        )

    def _scene_body(self, data: dict, script: str) -> str:
        title      = data.get("title", "Function Plot")
        function   = data.get("function", "np.sin(x)")
        x_min      = float(data.get("x_min", "-4"))
        x_max      = float(data.get("x_max", "4"))
        y_min      = float(data.get("y_min", "-2"))
        y_max      = float(data.get("y_max", "2"))
        x_label    = data.get("x_label", "x")
        y_label    = data.get("y_label", "y")
        color      = data.get("color", "BLUE")
        caption    = data.get("caption", "")
        narrations = data.get("narrations", {})

        n_axes    = narrations.get("axes",    "Let us set up the coordinate axes.")
        n_graph   = narrations.get("graph",   "Here is the function plotted on the graph.")
        n_caption = narrations.get("caption", caption or "")
        title_fs  = self._title_font_size(title)

        return (
            f"        import numpy as np\n"
            f"\n"
            f"        title = Text({title!r}, font_size={title_fs}, color=WHITE, weight=BOLD)\n"
            f"        title.to_edge(UP, buff=0.35)\n"
            f"        self.play(Write(title), run_time=0.8, rate_func=smooth)\n"
            f"        self.wait(0.3)\n"
            f"\n"
            f"        axes = Axes(\n"
            f"            x_range=[{x_min}, {x_max}, ({x_max}-({x_min}))/8],\n"
            f"            y_range=[{y_min}, {y_max}, ({y_max}-({y_min}))/6],\n"
            f"            x_length=10, y_length=5.0,\n"
            f"            axis_config={{'color': '#666688', 'stroke_width': 2}},\n"
            f"            tips=True,\n"
            f"        )\n"
            f"        axes.next_to(title, DOWN, buff=0.25)\n"
            f"        x_lbl = axes.get_x_axis_label(\n"
            f"            Text({x_label!r}, font_size=22, color='#a0a8d0'), edge=RIGHT, direction=RIGHT)\n"
            f"        y_lbl = axes.get_y_axis_label(\n"
            f"            Text({y_label!r}, font_size=22, color='#a0a8d0'), edge=UP, direction=UP)\n"
            f"\n"
            f"        with self.voiceover(text={n_axes!r}):\n"
            f"            self.play(\n"
            f"                AnimationGroup(Create(axes), Write(x_lbl), Write(y_lbl), lag_ratio=0.2),\n"
            f"                run_time=1.1, rate_func=smooth,\n"
            f"            )\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        graph = axes.plot(lambda x: {function}, color={color}, stroke_width=3)\n"
            f"        with self.voiceover(text={n_graph!r}):\n"
            f"            self.play(Create(graph), run_time=2.0, rate_func=smooth)\n"
            f"            self.wait(0.3)\n"
            f"\n"
            f"        if {caption!r}:\n"
            f"            caption_obj = Text({caption!r}, font_size=22, color='#a0a8d0')\n"
            f"            caption_obj.to_edge(DOWN, buff=0.3)\n"
            f"            with self.voiceover(text={n_caption!r}):\n"
            f"                self.play(FadeIn(caption_obj, shift=UP * 0.12), run_time=0.6, rate_func=smooth)\n"
            f"                self.wait(0.3)\n"
            f"\n"
            f"        self.wait(2)\n"
            f"        self.play(FadeOut(*self.mobjects), run_time=0.8)\n"
        )
