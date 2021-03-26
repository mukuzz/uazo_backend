from rest_framework import serializers
from mes.models import ProductionOrder, Style, ProductionSession, QcInput, Defect, Operation, SizeQuantity, Line, Buyer, StyleCategory, QcAppState, OperationDefect


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'


class ProductionOrderSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer()
    class Meta:
        model = ProductionOrder
        fields = '__all__'


class SizeQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeQuantity
        fields = ['id', 'size', 'quantity']


class StyleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StyleCategory
        fields = '__all__'


class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = '__all__'


class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'


class StyleSerializer(serializers.ModelSerializer):
    size_quantities = SizeQuantitySerializer(source='sizequantity_set', many=True, read_only=True)
    category = StyleCategorySerializer()
    defects = DefectSerializer(many=True, read_only=True)
    operations = OperationSerializer(many=True, read_only=True)
    order_details = ProductionOrderSerializer(source='order', read_only=True)

    class Meta:
        model = Style
        fields = '__all__'


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = '__all__'


class ProductionSessionSerializer(serializers.ModelSerializer):
    line = LineSerializer()
    class Meta:
        model = ProductionSession
        fields = '__all__'


class OperationDefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationDefect
        fields = '__all__'


class OperationDefectPKSerializer(serializers.Serializer):
    operation_id = serializers.IntegerField(required=False)
    defect_id = serializers.IntegerField()

class QcInputSerializer(serializers.ModelSerializer):
    defect_ids = serializers.PrimaryKeyRelatedField(queryset=Defect.objects.all(), many=True, write_only=True, required=False)
    defects = DefectSerializer(many=True, read_only=True)
    operation_defects_ids = OperationDefectPKSerializer(many=True, required=False)
    operation_defects = OperationDefectSerializer(many=True, read_only=True)
    id = serializers.CharField(required=True, max_length=36)

    class Meta:
        model = QcInput
        fields = '__all__'
    
    def create(self, validated_data):
        # if validated_data['input_type'] == 'defective' and len(validated_data['defect_ids']) == 0:
        #     raise serializers.ValidationError({"defect_ids": ["defects must be provided with defective input type"]})
        # Remove defect_ids field from validated_data to prevent
        # framework from trying to insert it in the QcInput model
        # which doesn't have the defect_ids field
        try:
            defect_ids = validated_data.pop('defect_ids')
        except KeyError:
            defect_ids = []
        try:
            operation_defects_ids = validated_data.pop('operation_defects_ids')
        except KeyError:
            operation_defects_ids = []
        qc_input = QcInput.objects.create(**validated_data)
        if validated_data['input_type'] == 'defective':
            # TODO: Remove after app is updated everywhere
            # For un updated apps sending only defect ids
            if len(operation_defects_ids) == 0:
                for defect in defect_ids:
                    operation_defect = OperationDefect.objects.get(operation=None, defect=defect)
                    qc_input.operation_defects.add(operation_defect)
            # For updated apps sending operation and defect ids
            else:
                for operation_defect_ids in operation_defects_ids:
                    try:
                        operation_id = operation_defect_ids['operation_id']
                    except KeyError:
                        operation_id = None
                    try:
                        defect_id = operation_defect_ids['defect_id']
                    except KeyError:
                        defect_id = None
                    operation_defect = OperationDefect.objects.get(operation__id=operation_id, defect__id=defect_id)
                    qc_input.operation_defects.add(operation_defect)
        return qc_input


class QcAppStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QcAppState
        fields = '__all__'