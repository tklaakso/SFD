from rest_framework import serializers

class AddressSerializer(serializers.Serializer):
    street_name = serializers.CharField(max_length = 50, required = True)
    street_num = serializers.CharField(max_length = 10, required = True)
    city = serializers.CharField(max_length = 50, required = True)
    province = serializers.CharField(max_length = 30, required = True)
    postal_code = serializers.CharField(max_length = 10, required = True)
    country = serializers.CharField(max_length = 30, required = True)
    unit = serializers.CharField(max_length = 100, required = False, allow_blank = True)
