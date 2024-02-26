import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime, timedelta

class ExchangeRateProvider(ABC):
    @abstractmethod
    async def get_exchange_rate(self, currency: str, date: str) -> Dict:
        pass

class PrivatBankAPI(ExchangeRateProvider):
    async def get_exchange_rate(self, currency: str, date: str) -> Dict:
        url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"Failed to fetch data for {currency} on date {date}")

class CurrencyConverter:
    def __init__(self, exchange_rate_provider: ExchangeRateProvider):
        self.exchange_rate_provider = exchange_rate_provider

    async def get_rates(self, currency: str, days: int) -> Dict:
        current_date = datetime.now().date()
        rates = []
        for i in range(days):
            date = (current_date - timedelta(days=i)).strftime("%d.%m.%Y")
            rate = await self.exchange_rate_provider.get_exchange_rate(currency, date)
            rates.append({date: rate})
        return rates

async def main():
    try:
        privat_bank_api = PrivatBankAPI()
        currency_converter = CurrencyConverter(privat_bank_api)

        days = int(input("Enter the number of days (1-10): "))
        if days < 1 or days > 10:
            print("Number of days must be between 1 and 10")
            return

        eur_rates = await currency_converter.get_rates('EUR', days)
        usd_rates = await currency_converter.get_rates('USD', days)

        print("EUR rates for the last", days, "days:")
        for rate in eur_rates:
            date = list(rate.keys())[0]
            eur_rate = next((x for x in rate[date]['exchangeRate'] if x['currency'] == 'EUR'), None)
            if eur_rate:
                print(f"{date}: {eur_rate['saleRate']} (sale) - {eur_rate['purchaseRate']} (purchase)")

        print("\nUSD rates for the last", days, "days:")
        for rate in usd_rates:
            date = list(rate.keys())[0]
            usd_rate = next((x for x in rate[date]['exchangeRate'] if x['currency'] == 'USD'), None)
            if usd_rate:
                print(f"{date}: {usd_rate['saleRate']} (sale) - {usd_rate['purchaseRate']} (purchase)")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())

