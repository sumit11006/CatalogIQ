import asyncio

from app.services.enrichment_ai import service


async def main():
    print("available:", service.is_available)
    try:
        out = await service.generate_json('Return exactly this JSON: {"ok": true}')
        print("OK:", out)
    except Exception as e:
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e)[:1000])


asyncio.run(main())
