from django.test import TestCase
from exchanges.models import Currency
from exchanges.templatetags.exchanges_tags import code_to_name


class ExchangesTemplatetagsTestCase(TestCase):
    def setUp(self):
        Currency.objects.create(name="Dollar", code="USD", sign="$", sign_after=False)
        Currency.objects.create(name="Złoty", code="PLN", sign="zł")
        Currency.objects.create(name="Bitcoin", code="BTC", sign="BTC", crypto=True)

        self.btc = Currency.objects.get(code="BTC")
        self.usd = Currency.objects.get(code="USD")

    def test_code_to_name_return_na_for_not_existing_code(self):
        code = "ZEC"

        result = code_to_name(code)
        print(result)
        self.assertEquals(result, 'N/A')

    def test_code_to_name_returns_name_for_valid_code(self):
        self.assertEquals(code_to_name("USD"), 'Dollar')
        self.assertEquals(code_to_name("PLN"), 'Złoty')
        self.assertEquals(code_to_name("BTC"), 'Bitcoin')

