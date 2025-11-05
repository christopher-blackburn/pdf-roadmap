from roadmapper_example import build_roadmap_from_definition, load_config
from pathlib import Path
import yaml

def main():
    config_path = Path(__file__).with_name("use_case_roadmap.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        use_case_config = yaml.safe_load(handle)

    roadmap = build_roadmap_from_definition(use_case_config, use_case_config)
    roadmap.draw()
    roadmap.save("ai_use_case_roadmap.png")
    roadmap.save("ai_use_case_roadmap.pdf")

if __name__ == "__main__":
    main()
