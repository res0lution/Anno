from rest_framework import serializers

from main.models import Anno, Comment


class AnnoSerializer(serializers.ModelSerializer):


    class Meta:
        model = Anno
        fields = ('id', 'title', 'content', 'price', 'created_at') 


class AnnoDetailSerializer(serializers.ModelSerializer):


    class Meta:
        model = Anno
        fields = ('id', 'title', 'content', 'price', 'created_at', 'contacts', 'image')



class CommentSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Comment
        fields = ('anno', 'author', 'content', 'created_at') 