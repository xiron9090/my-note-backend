import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Profile


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    users = graphene.List(UserType)
    profiles = graphene.List(ProfileType)
    me = graphene.Field(UserType)

    def resolve_profiles(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login pleaces')

        return Profile.objects.filter(user=user)

    def resolve_me(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login pleace')
        return user

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login pleaces')
        if not user.is_superuser:
            raise GraphQLError('You are not admin')

        return get_user_model().objects.get(id=kwargs.get('id'))

    def resolve_users(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login pleaces')
        if not user.is_superuser:
            raise GraphQLError('You are not admin')
        return get_user_model().objects.all()


class UserCreate(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        user = get_user_model()(username=kwargs.get('username'), email=kwargs.get('email'))
        user.set_password(kwargs.get('password'))
        user.save()
        return UserCreate(user=user)


class ProfileCreate(graphene.Mutation):
    profile = graphene.Field(ProfileType)

    class Arguments:

        avatar = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for create you profile')
        avatar = info.context.build_absolute_uri(settings.MEDIA_URL)

        profile = Profile(avatar=avatar+'avatar/' +
                          kwargs.get('avatar'), user=user)
        profile.save()
        return ProfileCreate(profile=profile)


class Mutation(graphene.ObjectType):
    profile_create = ProfileCreate.Field()
    user_create = UserCreate.Field()
