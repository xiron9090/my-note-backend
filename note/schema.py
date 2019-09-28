import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from django.db.models import Q
from .models import Category, Note
from django.contrib.auth.models import User


class NoteType(DjangoObjectType):
    class Meta:
        model = Note


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class Query(graphene.ObjectType):

    notes = graphene.List(NoteType, search=graphene.String())
    note = graphene.Field(NoteType, id=graphene.Int(required=True))
    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))

    def resolve_category(self, info, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('Login pleace')
        return Category.objects.get(id=kwargs.get('id'), user=user)

    def resolve_note(self, info, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('Login pleace')

        return Note.objects.get(id=kwargs.get('id'), user=user)

    def resolve_notes(self, info, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('Login pleace')

        if kwargs.get('search'):
            filter = (
                Q(title__icontains=kwargs.get('search')) |
                Q(note__icontains=kwargs.get('search')) |
                Q(category__name__icontains=kwargs.get('search')) |
                Q(user__username__icontains=kwargs.get('search'))
            )
            return Note.objects.filter(filter, user=user)
        return Note.objects.filter(user=user)

    def resolve_categories(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login pleace')
        return Category.objects.filter(user=user)


class CategoryCreate(graphene.Mutation):
    category = graphene.Field(CategoryType)

    class Arguments:
        name = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for create category')
        category = Category(name=kwargs.get('name'), user=user)
        category.save()
        return CategoryCreate(category=category)


class CategoryUpdate(graphene.Mutation):
    category = graphene.Field(CategoryType)

    class Arguments:
        category_id = graphene.Int(required=True)
        name = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for update category')
        category = Category.objects.get(
            id=kwargs.get('category_id'), user=user)
        category.name = kwargs.get('name')
        category.save()
        return CategoryUpdate(category=category)


class NoteCreate(graphene.Mutation):
    note = graphene.Field(NoteType)

    class Arguments:
        title = graphene.String(required=True)
        note = graphene.String(required=True)
        category = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for create note')
        category = Category.objects.get(name=kwargs.get('category'), user=user)
        note = Note(title=kwargs.get('title'), note=kwargs.get(
            'note'), category=category, user=user)
        note.save()
        return NoteCreate(note=note)


class NoteUpdate(graphene.Mutation):
    note = graphene.Field(NoteType)

    class Arguments:
        note_id = graphene.Int(required=True)
        title = graphene.String()
        note = graphene.String()
        category = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for update note')
        category = Category.objects.get(name=kwargs.get('category'), user=user)
        note = Note.objects.get(id=kwargs.get('note_id'), user=user)
        note.title = kwargs.get('title')
        note.note = kwargs.get('note')
        note.category = category
        note.save()
        return NoteUpdate(note=note)


class NoteDelete(graphene.Mutation):
    note_id = graphene.Int()

    class Arguments:
        note_id = graphene.Int(required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for create note')
        note = Note.objects.get(id=kwargs.get('note_id'), user=user)
        note.delete()
        return NoteDelete(note_id=kwargs.get('note_id'))


class CategoryDelete(graphene.Mutation):
    category_id = graphene.Int()

    class Arguments:
        category_id = graphene.Int(required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Login for delete category')
        category = Category.objects.get(
            id=kwargs.get('category_id'), user=user)
        category.delete()
        return CategoryDelete(category_id=kwargs.get('category_id'))


class Mutation(graphene.ObjectType):
    category_create = CategoryCreate.Field()
    category_update = CategoryUpdate.Field()
    category_delete = CategoryDelete.Field()
    note_create = NoteCreate.Field()
    note_update = NoteUpdate.Field()
    note_delete = NoteDelete.Field()
