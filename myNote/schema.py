import graphene
import graphql_jwt
import note.schema
import users.schema



class Query(users.schema.Query,note.schema.Query, graphene.ObjectType):
    pass


class Mutation(note.schema.Mutation,users.schema.Mutation,graphene.ObjectType):
    token = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
