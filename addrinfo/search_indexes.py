# coding:utf-8
import jieba
from haystack import indexes
#from haystack import site
from addrinfo.models import BusinessCircle
from haystack.query import SQ
from haystack.query import SearchQuerySet
#import addrinfo.models as models

class search_indexes(indexes.SearchIndex, indexes.Indexable):
    import sys  
    reload(sys)  
    sys.setdefaultencoding('utf8') 
    text = indexes.CharField(document=True, use_template=True)
    bc_name = indexes.CharField(model_attr='bc_name')
    bc_address = indexes.CharField(model_attr='bc_address')
    community_id = indexes.CharField(model_attr='community_id')
#    if bc_describe is None:
#        bc_describe=''
    def get_model(self):
        return BusinessCircle

    def index_queryset(self,using=None,community=None):
#        """Used when the entire index for model is updated."""
#        search_str = '建设'
#        seglist=jieba.cut_for_search(search_str)
#        search_method = SQ(bc_address__icontains= search_str )|SQ(bc_name__icontains= search_str )
#        for w in seglist:
#            print w
#            search_method = search_method | SQ(bc_address__icontains= w )|SQ(bc_name__icontains= w )
        if community == None:
            return self.get_model().objects.all().exclude(bc_address = None)
        else:
            return self.get_model().objects.filter(community_id = community).exclude(bc_address = None)
#filter(bc_name__icontains='建设')
#.exclude(bc_address = None)

#    def load_all_queryset(self):
        # Pull all objects related to the Note in search results.
#        return Note.objects.all().select_related()
#site.register(models.Post, PostIndex)



#class business_indexes(indexes.SearchIndex, indexes.Indexable):
#    import sys
#    reload(sys)
#    sys.setdefaultencoding('utf8')
#    text = indexes.CharField(document=True, use_template=True)
#    bc_name = indexes.CharField(model_attr='bc_name')
#    bc_address = indexes.CharField(model_attr='bc_address')
#    community_id = indexes.CharField(model_attr='community_id')
#    def get_model(self):
#        return BusinessCircle
#    def index_queryset(self, using=None):
#        return self.get_model().objects.filter(community_id = 1).exclude(bc_address = None)
