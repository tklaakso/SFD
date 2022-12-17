from rest_framework import serializers

class AddressSerializer(serializers.Serializer):
    street_name = serializers.CharField(max_length = 50, required = True)
    street_num = serializers.IntegerField( required = True)
    city = serializers.CharField(max_length = 50, required = True)
    province = serializers.CharField(max_length = 30, required = True)
    postal_code = serializers.CharField(max_length = 6, required = True)