from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Answer, Category, Question, File

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file_id', 'file_name', 's3_object_name', 'created_date')


class AnswerSerializer(serializers.ModelSerializer):
    # question_id = serializers.PrimaryKeyRelatedField(source='question', queryset=Question.objects.all(), required=False)
    # user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), required=False)
    attachments = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = (
            'answer_id',
            'question_id',
            'created_timestamp',
            'updated_timestamp',
            'user_id',
            'answer_text',
            'attachments'
        )
        # extra_kwargs = {
        #     'question': {'required': False}
        # }


class QuestionSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    answers = AnswerSerializer(many=True, required=False)
    # user_id = serializers.PrimaryKeyRelatedField(source='user', queryset=User.objects.all(), required=False)
    attachments = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['question_id', 'created_timestamp', 'updated_timestamp',
                  'user_id', 'question_text', 'categories', 'answers', 'attachments']
        # extra_kwargs = {
        #     'categories': {'allow_empty': True}
        # }\

    def create(self, validated_data):
        user_id = validated_data['user_id']
        categories = validated_data.pop('categories', {})
        answers = validated_data.pop('answers', {})
        q = Question.objects.create(**validated_data)
        for v in categories:
            if Category.objects.filter(category=v['category']):
                category = Category.objects.filter(category=v['category'])[0]
                category.questions.add(q)
            else:
                category = Category.objects.create(category=v['category'])
                category.questions.add(q)
            category.save()
        for v in answers:
            Answer.objects.create(
                answer_text=v['answer_text'], user_id=user_id, question_id=q.pk)

        return q

    def update(self, instance, validated_data):
        instance.question_text = validated_data.get(
            'question_text', instance.question_text)
        categories = validated_data.pop('categories', {})
        if categories:
            instance.categories.clear()
            instance.save()
            for v in categories:
                if Category.objects.filter(category=v['category']):
                    category = Category.objects.filter(
                        category=v['category'])[0]
                    category.questions.add(instance)
                else:
                    category = Category.objects.create(category=v['category'])
                    category.questions.add(instance)
            category.save()
            instance.updated_timestamp = timezone.now()
            instance.save()
        return instance
