import subprocess
from pathlib import Path

def run_java_class() -> str:
    print("🚀 Start running Java class TikTokAnalysis...")

    classpath = (
        "/Users/lennartmac/Documents/Projects/insta/target/classes:"
        "/Users/lennartmac/.m2/repository/mysql/mysql-connector-java/8.0.27/mysql-connector-java-8.0.27.jar"
    )
    java_class = "com.lennart.model.tiktok.TikTokAnalysis"

    result = subprocess.run(
        ["java", "-cp", classpath, java_class],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Fout bij uitvoeren van Java class:")
        print(result.stderr)
        return ""

    print("✅ Java class finished successfully")
    print(f"ℹ️ Aantal regels output: {len(result.stdout.splitlines())}")
    return result.stdout

def save_output_to_file(output_text: str):
    if not output_text:
        print("⚠️ Geen data om op te slaan")
        return

    print("💾 Opslaan van output naar tiktok_usernames.txt...")

    input_file = Path("../apify_input/tiktok_usernames.txt")
    input_file.parent.mkdir(parents=True, exist_ok=True)

    with open(input_file, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"✅ Data is opgeslagen in {input_file.resolve()}")
    print("📋 Eerste 10 regels van het bestand:")
    for i, line in enumerate(output_text.splitlines(), start=1):
        print(line)
        if i >= 10:
            break

def main():
    print("🟢 Script gestart\n")

    java_output = run_java_class()

    print("\n📂 Verwerken van Java output...")
    save_output_to_file(java_output)

    print("\n🎉 Script voltooid!")

if __name__ == "__main__":
    main()
