import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
from graphene_file_upload.scalars import Upload
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Profile
from note.models import Category, Note


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    users = graphene.List(UserType)
    profile = graphene.List(ProfileType)
    me = graphene.Field(UserType)

    def resolve_profile(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login please')
        if user.is_superuser:
            return Profile.objects.all()
        return Profile.objects.filter(user=user)

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login please')
        return user

    def resolve_user(self, info, **kwargs):

        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('Login pleace')

        return User.objects.get(id=kwargs.get('id'), username=user)

    def resolve_users(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login pleaces')
        if not user.is_superuser:
            raise GraphQLError('You are not admin')
        return User.objects.all()


class UserCreate(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        file = Upload()

    def mutate(self, info, file, **kwargs):
        user = User(username=kwargs.get('username'), email=kwargs.get('email'))
        user.set_password(kwargs.get('password'))
        user.save()
        avatar = info.context.build_absolute_uri(settings.MEDIA_URL)
        profile = Profile(avatar=avatar+'avatar/' + file.name, user=user)
        profile.save()
        fs = FileSystemStorage()

        fs.save('avatar/'+file.name, file)
        return UserCreate(user=user)


class UserDelete(graphene.Mutation):
    user_id = graphene.Int()

    class Arguments:
        user_id = graphene.Int(required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for delete your user')
        user_del = User.objects.get(id=kwargs.get('user_id'))

        if user.is_superuser:
            user_del.delete()

        elif user == user_del:
            user_del.delete()

        else:
            raise GraphQLError('only can delete your user')
        return UserDelete(user_id=kwargs.get('user_id'))


class ProfileUpdate(graphene.Mutation):
    profile = graphene.Field(ProfileType)

    class Arguments:

        file = Upload()

    def mutate(self, info, file, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login fro update your profile')

        profile = Profile.objects.get(user=user)
        avatar = info.context.build_absolute_uri(settings.MEDIA_URL)
        profile.avatar = avatar+'avatar/' + file.name
        profile.save()

        fs = FileSystemStorage()

        fs.save('avatar/'+file.name, file)

        return ProfileUpdate(profile=profile)


class Mutation(graphene.ObjectType):
    user_create = UserCreate.Field()
    user_delete = UserDelete.Field()
    profile_update = ProfileUpdate.Field()
