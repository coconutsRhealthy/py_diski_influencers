from util.new_insta_influ_research import insta_username_analysis
from util.new_insta_influ_research import run_save_java_insta_accfinder

if __name__ == "__main__":
    print("🟢 Pipeline gestart\n")

    print("🚀 Running run_save_java_insta_accfinder ...")
    try:
        run_save_java_insta_accfinder.main()
    except Exception as e:
        print(f"❌ Fout bij insta_username_analysis: {e}")
        exit(1)

    print("\n🚀 Running insta_username_analysis.py ...")
    try:
        insta_username_analysis.main()
    except Exception as e:
        print(f"❌ Fout bij run_insta_java: {e}")
        exit(1)

    print("\n🎉 Pipeline voltooid!")
