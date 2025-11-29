import asyncio
import os
from dotenv import load_dotenv

from agents import Runner, set_default_openai_key
from custom_agents.scraper import scraper
from custom_agents.consolidator import consolidator
from custom_agents.xlsm_cleaner import xlsm_cleaner
from tools.browser.controller import close_browser
from tools.merger import merge_and_clean_csvs


async def main():
    load_dotenv()
    set_default_openai_key(os.getenv("OPENAI_API_KEY"))

    print("🚀 Agente autónomo iniciado...\n")
    # objetivo = input("🎯 Objetivo del agente: ")
    objetivo = "Segmento 1, fecha más reciente"
    print(f"🎯 Objetivo: {objetivo}")

    skip_scraper = True  # Hardcoded variable to skip scraper

    if not skip_scraper:
        print("🕷️ Ejecutando Scraper...")
        result_scraper = await Runner.run(
            starting_agent=scraper,
            input=objetivo,
            max_turns=40,
        )

        print("\n" + "=" * 70)
        print(f"🏁 Resultado Scraper: {result_scraper.final_output}")

        await close_browser()
    else:
         print("⏭️ Saltando Scraper...")

    # print("\n🤖 Ejecutando Consolidator...")
    # # The consolidator needs to know the objective to filter files
    # result_consolidator = await Runner.run(
    #     starting_agent=consolidator,
    #     input=f"Objetivo original: {objetivo}. Por favor consolida la información descargada.",
    #     max_turns=40,
    # )

    # print("\n" + "=" * 70)
    # print(f"🏁 Resultado Consolidator: {result_consolidator}")

    # Quick test flags (set to True to run only the merge step)
    run_merge_only = True

    if run_merge_only:
        print("\n🔁 Ejecutando solo merge_and_clean_csvs (Modo Prueba)...")
        res = merge_and_clean_csvs(
            temp_folder="data/preprocessed/temp/",
            output_folder="data/preprocessed/",
            output_filename="Consolidated_Test.csv"
        )
        print(f"🏁 Resultado merge: {res}")
        return

    print("\n🧹 Ejecutando XlsmCleaner (Modo Prueba)...")
    result_cleaner = await Runner.run(
        starting_agent=xlsm_cleaner,
        input="data/preprocessed/temp/",
        max_turns=40,
    )
    print(f"🏁 Resultado Cleaner: {result_cleaner.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
