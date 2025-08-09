import graphene

#["class Query(CRMQuery, graphene.ObjectType)"]
#["from crm.schema import"]
class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=Query)