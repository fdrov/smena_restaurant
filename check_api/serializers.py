from rest_framework.serializers import Serializer, CharField, IntegerField


class ItemSerializer(Serializer):
    name = CharField()
    quantity = IntegerField(min_value=1)
    unit_price = IntegerField(min_value=0)


class ClientSerializer(Serializer):
    name = CharField()
    phone = CharField()


class OrderSerializer(Serializer):
    items = ItemSerializer(
        many=True,
        allow_empty=False,
    )
    client = ClientSerializer()
    id = IntegerField()
    price = IntegerField(min_value=0)
    address = CharField()
    point_id = IntegerField()


class ApiKeySerializer(Serializer):
    api_key = CharField()


class GetPdfSerializer(Serializer):
    api_key = CharField()
    check_id = IntegerField()
