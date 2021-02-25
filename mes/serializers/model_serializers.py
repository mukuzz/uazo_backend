from rest_framework import serializers
from mes.models import ProductionOrder, Style, ProductionSession, QcInput, Defect

class ProductionOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionOrder
        fields = '__all__'


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'


class ProductionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionSession
        fields = '__all__'


class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = '__all__'


class QcInputSerializer(serializers.ModelSerializer):
    defect_ids = serializers.PrimaryKeyRelatedField(queryset=Defect.objects.all(), many=True, write_only=True)
    defects = DefectSerializer(many=True, read_only=True)

    class Meta:
        model = QcInput
        fields = '__all__'
    
    def create(self, validated_data):
        # if validated_data['input_type'] == 'defective' and len(validated_data['defect_ids']) == 0:
        #     raise serializers.ValidationError({"defect_ids": ["defects must be provided with defective input type"]})
        # Remove defect_ids field from validated_data to prevent
        # framework from trying to insert it in the QcInput model
        # which doesn't have the defect_ids field
        defect_ids = validated_data.pop('defect_ids')
        qc_input = QcInput.objects.create(**validated_data)
        if validated_data['input_type'] == 'defective': 
            for defect_id in defect_ids:
                qc_input.defects.add(defect_id)
        return qc_input