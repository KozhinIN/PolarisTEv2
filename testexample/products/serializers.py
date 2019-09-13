from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField
from .models import *

class PenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pen
        fields = ('product','color', 'type')
        extra_kwargs = {'product': {'write_only': True, 'required': True}}

class PencilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pencil
        fields = ('product','color', 'hardness')
        extra_kwargs = {'product': {'write_only': True, 'required': True}}

class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ('product', 'format', 'sheets')
        extra_kwargs = {'product': {'write_only': True, 'required': True}}

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'brand', 'vendorcode', 'price', 'description')

class ProductReadSerializer(serializers.ModelSerializer):
    pendetail = PenSerializer(read_only=True)
    pencildetail = PencilSerializer(read_only=True)
    paperdetail = PaperSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'brand', 'vendorcode','price', 'description', 'pendetail', 'pencildetail', 'paperdetail')

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is not None:
                represenation = field.to_representation(attribute)
                if represenation is None:
                    # Do not seralize empty objects
                    continue
                if isinstance(represenation, list) and not represenation:
                   # Do not serialize empty lists
                   continue
                ret[field.field_name] = represenation

        return ret