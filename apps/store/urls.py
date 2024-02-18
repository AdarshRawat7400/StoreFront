from django.urls import path
from .views import CategoryCreateView, CategoryDataView, CategoryTemplateView, CategoryUpdateView, CmsSocialsTemplateView, ContactQueriesDataView, ContactQueriesTemplateView, FeedbackDataView, FeedbackTemplateView, HandleContactQueryAnswerView, OrdersDataView, OrdersTemplateView, PageCreateView, PageDataView, PageTemplateView, PageUpdateView, ProductCreateView, ProductDataView, ProductListView, ProductDetailView,ManageSlidesView, ProductTemplateView, ProductUpdateView, RemoveImageView

app_name = 'store'

urlpatterns = [
    path('manage-slides/', ManageSlidesView.as_view(), name='manage_slides'),
    path('category/create/', CategoryCreateView.as_view(), name='create-category'),
    path('category/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/', CategoryTemplateView.as_view(), name='category-list'),
    path('category-list-data/', CategoryDataView.as_view(), name='category-list-data'),
    path('products/', ProductTemplateView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/edit/<int:pk>/', ProductUpdateView.as_view(), name='product-edit'),
    path('product-list-data/', ProductDataView.as_view(), name='product-list-data'),
    path('orders/', OrdersTemplateView.as_view(), name='orders'),
    path('orders/data/', OrdersDataView.as_view(), name='orders-data'),
    path('pages/', PageTemplateView.as_view(), name='page-list'),
    path('pages/create/', PageCreateView.as_view(), name='page-create'),
    path('pages/update/<int:pk>/', PageUpdateView.as_view(), name='page-update'),
    path('page-list-data/', PageDataView.as_view(), name='page-list-data'),
    path('feedbacks/', FeedbackTemplateView.as_view(), name='feedback-list'),
    path('feedback-list-data/', FeedbackDataView.as_view(), name='feedback-list-data'),
    path('contact-queries/', ContactQueriesTemplateView.as_view(), name='contact-queries-list'),
    path('contact-queries-data/', ContactQueriesDataView.as_view(), name='contact-queries-list-data'),
    path('handle-contact-query-answer/', HandleContactQueryAnswerView.as_view(), name='handle_contact_query_answer'),
    path('cms-socials/', CmsSocialsTemplateView.as_view(), name='cms-socials'),
    path('remove-image/', RemoveImageView.as_view(), name='remove-image'),
    # path('products/', ProductListView.as_view(), name='product_list'),
    # path('<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    # path('<int:id>/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),


]
