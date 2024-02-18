from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.utils.translation import gettext as _
from django.utils.html import escape
from django.utils.html import format_html
from django_countries.serializers import CountryFieldMixin
from django.template.loader import render_to_string
from django.http import JsonResponse
from apps.store.forms import SlideForm
from apps.core.auth_mixins import CheckRolesMixin
from apps.users.models import Users
from .models import BillingAddress, Category, CmsSocials, ContactQueries, Feedback, Order, Pages, Product, ProductImage, Slide, Tag
from django.views.generic.edit import FormMixin
from django.views.generic import DetailView
from django import forms
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from .models import Category
from .forms import AnswerQueryForm, CategoryCreateForm, CategoryEditForm, CmsSocialsForm, CreatePagesForm, ProductCreateForm, ProductUpdateForm, UpdatePagesForm
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.urls import reverse,reverse_lazy






class ProductListView(ListView, FormMixin):
    model = Product
    template_name = 'store/product/list.html'
    context_object_name = 'products'
    paginate_by = 20
    form_class = forms.Form  # Set a generic form class


    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            return Product.objects.filter(category=category, available=True)
        else:
            return Product.objects.filter(available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product/detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(available=True)

    def get_object(self, queryset=None):
        # Customize the queryset based on your requirements
        return get_object_or_404(Product, id=self.kwargs['id'], slug=self.kwargs['slug'], available=True)


class ManageSlidesView(CheckRolesMixin,TemplateView,View):
    template_name = 'backend/store/manage_slides.html'
    form_class = SlideForm
    allowed_roles = ('admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slides'] = Slide.objects.all()
        context['create_slide_form'] = self.form_class()
        context['success'] = None
        return context
    


    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')
        slide_id = request.GET.get('slide_id')
        
        if action == 'delete':
            # Handle delete action
            slide = get_object_or_404(Slide, pk=slide_id)
            slide.delete()
            messages.success(request, 'Slide deleted successfully.')
        elif action == 'status':
            # Handle activate action
            slide = get_object_or_404(Slide, pk=slide_id)
            slide.is_active = not slide.is_active
            slide.save()
            messages.success(request, 'Slide status updated successfully.')
        
        return self.render_to_response(self.get_context_data(success=True))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            form.cleaned_data['slide_id'] = request.POST.get('slide_id')
            form.save()
            messages.success(request, 'Slide created successfully!')
            
            # Redirect after a successful form submission
            return redirect('store:manage_slides')
        else:
            # Render the same page with the form and errors
            messages.error(request, 'There was an error in the form submission. Please check the errors.')
            return render(request, self.template_name, self.get_context_data(form=form,success="Sdadas"))

    # def put(self, request, slide_id, *args, **kwargs):
    #     slide = Slide.objects.get(pk=slide_id)
    #     form = self.form_class(request.POST, request.FILES, instance=slide)
    #     if form.is_valid():
    #         form.save()
    #         self.success_message = "Slide updated successfully!"
    #     else:
    #         self.success_message = None

    #     return self.render_to_response(self.get_context_data())
        



class CategoryCreateView(CheckRolesMixin,TemplateView, FormMixin):
    template_name = 'backend/store/category/category_create.html'
    form_class = CategoryCreateForm
    success_url = reverse_lazy('store:category-list')
    allowed_roles = ('admin',)


    def get(self, request, *args, **kwargs):
        form = self.get_form()
        return render(request, self.template_name, {'category_form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            # Save the form and redirect on success
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect(self.success_url)

        # Render the form with validation errors
        messages.error(request, 'Error creating category. Please check the form.')
        return render(request, self.template_name, {'category_form': form})


class CategoryUpdateView(CheckRolesMixin,TemplateView, FormMixin):
    template_name = 'backend/store/category/category_edit.html'
    form_class = CategoryEditForm
    success_url = reverse_lazy('store:category-list')
    allowed_roles = ('admin',)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        category = Category.objects.filter(pk=pk).first()
        action = request.GET.get('action')

        if action == 'delete':
            # Handle delete action
            category.delete()
            messages.success(request, 'Category deleted successfully.')
            return redirect('store:category-list')
        elif action == 'status':
            # Handle activate action
            category.is_active = not category.is_active
            category.save()
            messages.success(request, 'Category status updated successfully.')
            return redirect('store:category-list')


        form = CategoryEditForm(instance=category)
        return render(request, self.template_name, {'category_form': form, 'category': category})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        category = Category.objects.filter(pk=pk).first()
        form = CategoryEditForm(request.POST, request.FILES, instance=category)

        if form.is_valid():
            # Save the form and redirect on success
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect(self.success_url)

        # Render the form with validation errors
        messages.error(request, 'Error updating category. Please check the form.')
        return render(request, self.template_name, {'category_form': form, 'category': category})

class CategoryTemplateView(CheckRolesMixin,TemplateView):
    model = Category
    allowed_roles = ('admin',)
    template_name = 'backend/store/category/category_list.html'
    context_object_name = 'categories'



    
class CategoryDataView(CheckRolesMixin, BaseDatatableView, TemplateView):
    model = Category
    template_name = "backend/store/category/category_list.html"
    columns = ['id', 'name', 'description', 'slug', 'image', 'is_active', 'actions']  # Add 'actions' to columns
    order_columns = ['id', 'name', 'description', 'slug', 'image', 'is_active', '']  # Add '' for actions

    allowed_roles = ("admin",)




    def filter_queryset(self, qs):
        # qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(name__istartswith=sSearch) | Q(description__istartswith=sSearch) | Q(slug__istartswith=sSearch))
        return qs

    def render_column(self, row, column):
        # Handle the 'actions' column separately
        if column == 'image':
            if row.image:
                # Render the image column with the base64-encoded image
                image_data = row.image  # Assuming 'image' contains base64-encoded data
                image_tag = f'<a href="{row.image.url}" data-lightbox="category-images" data-title="{row.name}"><img src="{row.image.url}" alt="{row.name}" style="width: 100px; height: 50px;"></a>'
            else:
                # Render a placeholder or alternative content when image is not available
                image_tag = 'Image not available'
            return image_tag

        elif column == 'actions':
            return self.render_actions(row)
        elif column == 'is_active':
            # Render the active status column with corresponding icons
            if row.is_active:
                return '<i class="material-icons text-success">check_circle</i>'
            else:
                return '<i class="material-icons text-danger">cancel</i>'
        elif column == 'description':
            # Render a button to view the description
            description_button = f'<button class="btn btn-sm btn-primary view-description" data-row-id="{row.id}">View Description</button>'
            description_hidden = f'<div id="descriptionData-{row.id}" style="display: none;">{row.description}</div>'
            return description_button + description_hidden
        
        return super().render_column(row, column)

    def render_actions(self, row):
        category_id = row.id

        # Edit Button
        edit_url = reverse('store:category-edit', kwargs={'pk': category_id})
        edit_button = f'<a href="{edit_url}" class="btn btn-sm btn-warning">{_("Edit")}</a>'

        # Delete Button
        delete_url = reverse('store:category-edit', kwargs={'pk': category_id})
        delete_button = f'<a href="{delete_url}?action=delete" class="btn btn-sm btn-danger" data-confirm="{_("Are you sure you want to delete this category?")}">{_("Delete")}</a>'


        # Make Active/Inactive Button
        if row.is_active:
            status_url = reverse("store:category-edit", kwargs={"pk": category_id})
            status_button = f'<a href="{status_url}?action=status" class="btn btn-sm btn-success">{_("Make Inactive")}</a>'
        else:
            status_url = reverse("store:category-edit", kwargs={"pk": category_id})
            status_button = f'<a href="{status_url}?action=status" class="btn btn-sm btn-info">{_("Make Active")}</a>'


        return f'{edit_button} {delete_button} {status_button}'

    def get_initial_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datatable_options'] = {'searching': True, 'ordering': True, 'pageLength': 20}  # Customize DataTable options
        return context



class ProductTemplateView(CheckRolesMixin,TemplateView):
    model = Product
    allowed_roles = ('admin',)
    template_name = 'backend/store/product/product_list.html'
    context_object_name = 'products'



class ProductCreateView(CheckRolesMixin,TemplateView, FormMixin):
    template_name = 'backend/store/product/product_create.html'
    form_class = ProductCreateForm
    success_url = reverse_lazy('store:product-list')
    allowed_roles = ('admin',)

    def get(self, request, *args, **kwargs):
        # Assuming you have Customers in your database
        import random
        from datetime import datetime
        customers = Users.objects.filter(role='customer')
        form = self.get_form()
        return render(request, self.template_name, {'product_form': form})

    def post(self, request, *args, **kwargs):
        
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            messages.success(request, 'Product created successfully!')
            return JsonResponse({'success': True,'message': 'Product created successfully!', 'redirect_url': self.success_url})

        # If there's an error, return JSON response with error messages
        errors = {field: form.errors[field][0] for field in form.errors}
        return JsonResponse({'success': False, 'errors': errors}, status=400)



class ProductUpdateView(CheckRolesMixin,TemplateView, FormMixin):
    template_name = 'backend/store/product/product_edit.html'
    form_class = ProductUpdateForm
    success_url = reverse_lazy('store:product-list')
    allowed_roles = ('admin',)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        product = Product.objects.filter(pk=pk).first()
        action = request.GET.get('action')

        if action == 'delete':
            # Handle delete action
            product.delete()
            messages.success(request, 'Product deleted successfully.')
            return redirect('store:product-list')
        elif action == 'status':
            # Handle activate action
            product.is_active = not product.is_active
            product.save()
            messages.success(request, 'Product status updated successfully.')
            return redirect('store:product-list')


        form = ProductUpdateForm(instance=product)
        return render(request, self.template_name, {'product_form': form, 'product': product})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        product = Product.objects.filter(pk=pk).first()
        form = ProductUpdateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            instance = form.save()
            messages.success(request, 'Product updated successfully!')
            return JsonResponse({'success': True,'message': 'Product updated successfully!', 'redirect_url': self.success_url})

        # If there's an error, return JSON response with error messages
        errors = {field: form.errors[field][0] for field in form.errors}
        return JsonResponse({'success': False, 'errors': errors}, status=400)


class ProductDataView(CheckRolesMixin,BaseDatatableView):
    model = Product
    columns = ['id', 'name', 'price', 'category__name', 'stock_quantity', 'is_active','brand','is_featured','label','image','description_short']
    allowed_roles = ('admin',)
    def filter_queryset(self, qs):
        # qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(name__istartswith=sSearch) | Q(description_short__istartswith=sSearch) | Q(slug__istartswith=sSearch))
        return qs

    def render_column(self, row, column):
        # Handle the 'actions' column separately
        if column == 'image':
            if row.images.first():
                image_url = row.images.first().image.url
                # Render the image column with the base64-encoded image
                image_data = row.image  # Assuming 'image' contains base64-encoded data
                image_tag = f'<a href="{image_url}" data-lightbox="category-images" data-title="{row.name}"><img src="{image_url}" alt="{row.name}" style="width: 100px; height: 50px;"></a>'
            else:
                # Render a placeholder or alternative content when image is not available
                image_tag = 'Image not available'
            return image_tag

        elif column == 'actions':
            return self.render_actions(row)
        elif column == 'is_active':
            # Render the active status column with corresponding icons
            if row.is_active:
                return '<i class="material-icons text-success">check_circle</i>'
            else:
                return '<i class="material-icons text-danger">cancel</i>'
        elif column == 'is_featured':
            # Render the active status column with corresponding icons
            if row.is_featured:
                return '<i class="material-icons text-success">check_circle</i>'
            else:
                return '<i class="material-icons text-danger">cancel</i>'
        elif column == 'description':
            # Render a button to view the description
            description_button = f'<button class="btn btn-sm btn-primary view-description" data-row-id="{row.id}">View Description</button>'
            description_hidden = f'<div id="descriptionData-{row.id}" style="display: none;">{row.description}</div>'
            return description_button + description_hidden
        
        return super().render_column(row, column)

    def render_actions(self, row):
        product_id = row.id

        # Edit Button
        edit_url = reverse('store:product-edit', kwargs={'pk': product_id})
        edit_button = f'<a href="{edit_url}" class="btn btn-sm btn-warning">{_("Edit")}</a>'

        # Delete Button
        delete_url = reverse('store:product-edit', kwargs={'pk': product_id})
        delete_button = f'<a href="{delete_url}?action=delete" class="btn btn-sm btn-danger" data-confirm="{_("Are you sure you want to delete this category?")}">{_("Delete")}</a>'


        # Make Active/Inactive Button
        if row.is_active:
            status_url = reverse("store:product-edit", kwargs={"pk": product_id})
            status_button = f'<a href="{status_url}?action=status" class="btn btn-sm btn-success">{_("Make Inactive")}</a>'
        else:
            status_url = reverse("store:product-edit", kwargs={"pk": product_id})
            status_button = f'<a href="{status_url}?action=status" class="btn btn-sm btn-info">{_("Make Active")}</a>'


        return f'{edit_button} {delete_button} {status_button}'

    def get_initial_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datatable_options'] = {'searching': True, 'ordering': True, 'pageLength': 20}  # Customize DataTable options
        return context



class OrdersTemplateView(CheckRolesMixin, TemplateView):
    template_name = "backend/store/orders.html"
    allowed_roles = ("superadmin", "admin")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        # Add your context variables for rendering the template
        return context
    
class OrdersDataView(CheckRolesMixin, BaseDatatableView, TemplateView):
    # ... (existing code)

    model = Order
    columns = ["order_date", "id", "ref_code", "customer__username", "total_amount", "shipping_address__country", "billing_address__zip", "payment_status", "order_status", "delivery_date", "tracking_number"]
    order_columns = ["order_date", "id", "ref_code", "customer__username", "total_amount", "shipping_address__country", "billing_address__country", "billing_address__zip", "payment_status", "order_status", "delivery_date", "tracking_number"]
    allowed_roles = ("superadmin", "admin")


    def filter_queryset(self, qs):
        # qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            pass
            qs = qs.filter(Q(customer__username=sSearch) | Q(shipping_address__country=sSearch) | Q(payment_status=sSearch) | Q(tracking_number=sSearch))
        return qs

    def render_column(self, row, column):

        # Handle the 'actions' column separately
        if column == "actions":
            return format_html(
                """
                <div class="dropdown">
                    <button class="btn btn-primary dropdown-toggle" type="button" id="actionDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Actions
                    </button>
                    <div class="dropdown-menu" aria-labelledby="actionDropdown">
                        <a class="dropdown-item" href="{}" target="_blank">Download Invoice</a>
                        <a class="dropdown-item" href="{}">Mail Invoice</a>
                        <a class="dropdown-item refund-order" data-order-id="{}" href="#">Refund Order</a>
                    </div>
                </div>
                """,
                reverse("store:orders"), # skip for now
                reverse("store:orders"), # skip for now
                # reverse("store:download-=", kwargs={"pk": row.id}), # skip for now
                # reverse("store:mail-invoice", kwargs={"pk": row.id}), # skip for now
                row.id,
            )
        # Explicitly include attributes

        # Handle other columns


        if column == 'customer__username':
            return row.customer.username
        elif column == 'shipping_address__country':
            return row.shipping_address.country.code
        elif column == 'billing_address__zip':
            return row.billing_address.zip

        return super().render_column(row, column)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context variables for rendering the template
        return context
    
    def get_initial_queryset(self):
        return self.model.objects.all()
    


class PageTemplateView(CheckRolesMixin,TemplateView):
    model = Pages
    allowed_roles = ('admin',)
    template_name = 'backend/store/page/page_list.html'
    context_object_name = 'pages'



class PageCreateView(CheckRolesMixin,TemplateView, FormMixin):
    template_name = 'backend/store/page/page_create.html'
    form_class = CreatePagesForm
    success_url = reverse_lazy('store:page-list')
    allowed_roles = ('admin',)

    def get(self, request, *args, **kwargs):
        
        form = self.get_form()
        return render(request, self.template_name, {'page_form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()


        if form.is_valid():
            # Save the form and redirect on success
            form.save()
            messages.success(request, 'Page created successfully!')
            return redirect(self.success_url)

        # Render the form with validation errors
        messages.error(request, 'Error creating page. Please check the form.')
        return render(request, self.template_name, {'page_form': form})



class PageUpdateView(CheckRolesMixin,TemplateView, FormMixin):
    template_name = 'backend/store/page/page_edit.html'
    form_class = UpdatePagesForm
    success_url = reverse_lazy('store:page-list')
    allowed_roles = ('admin',)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        page = Pages.objects.filter(pk=pk).first()
        action = request.GET.get('action')

        if action == 'delete':
            # Handle delete action
            page.delete()
            messages.success(request, 'Page deleted successfully.')
            return redirect('store:page-list')
        elif action == 'status':
            # Handle activate action
            page.is_active = not page.is_active
            page.save()
            messages.success(request, 'Page status updated successfully.')
            return redirect('store:page-list')


        form = UpdatePagesForm(instance=page)
        return render(request, self.template_name, {'page_form': form, 'page': page})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        page = Pages.objects.filter(pk=pk).first()
        form = UpdatePagesForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            # Save the form and redirect on success
            form.save()
            messages.success(request, 'Page updated successfully!')
            return redirect(self.success_url)

        # Render the form with validation errors
        messages.error(request, 'Error updating page. Please check the form.')
        return render(request, self.template_name, {'page_form': form, 'page': page})




class PageDataView(CheckRolesMixin,BaseDatatableView):
    allowed_roles = ('admin',)
    model = Pages
    columns = ['id', 'name', 'slug', 'category', 'is_active', 'content','actions']

    def filter_queryset(self, qs):
        # qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            pass
            qs = qs.filter(Q(name__icontains=sSearch) | Q(category__icontains=sSearch))
        return qs



    def render_column(self, row, column):
        # Handle the 'actions' column separately
  

        if column == 'actions':
            return self.render_actions(row)
        elif column == 'is_active':
            # Render the active status column with corresponding icons
            if row.is_active:
                return '<i class="material-icons text-success">check_circle</i>'
            else:
                return '<i class="material-icons text-danger">cancel</i>'
        elif column == 'content':
            # Render a button to view the description
            content_button = f'<button class="btn btn-sm btn-primary view-description" data-row-id="{row.id}">View Content</button>'
            content_hidden = f'<div id="descriptionData-{row.id}" style="display: none;">{row.content}</div>'
            return content_button + content_hidden
        
        return super().render_column(row, column)

    def render_actions(self, row):
        page_id = row.id

        # Edit Button
        edit_url = reverse('store:page-update', kwargs={'pk': page_id})
        edit_button = f'<a href="{edit_url}" class="btn btn-sm btn-warning">{_("Edit")}</a>'

        # Delete Button
        delete_url = reverse('store:page-update', kwargs={'pk': page_id})
        delete_button = f'<a href="{delete_url}?action=delete" class="btn btn-sm btn-danger" data-confirm="{_("Are you sure you want to delete this category?")}">{_("Delete")}</a>'


        # Make Active/Inactive Button
        if row.is_active:
            status_url = reverse("store:page-update", kwargs={"pk": page_id})
            status_button = f'<a href="{status_url}?action=status" class="btn btn-sm btn-success">{_("Make Inactive")}</a>'
        else:
            status_url = reverse("store:page-update", kwargs={"pk": page_id})
            status_button = f'<a href="{status_url}?action=status" class="btn btn-sm btn-info">{_("Make Active")}</a>'


        return f'{edit_button} {delete_button} {status_button}'
    


class FeedbackTemplateView(CheckRolesMixin,TemplateView,View):
    allowed_roles = ('admin',)
    model = Feedback
    template_name = 'backend/store/feedback/feedback_list.html'
    context_object_name = 'feedbacks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action = self.request.GET.get('action')
        pk = self.request.GET.get('pk')
        if action == 'delete':
            page = Feedback.objects.filter(id=pk).first()
            if page:
                page.delete()
            messages.success(self.request, 'Page deleted successfully.')
                  
        return context



class FeedbackDataView(CheckRolesMixin,BaseDatatableView):
    allowed_roles = ('admin',)
    model = Feedback  # Replace with your actual feedback model
    columns = ['id', 'email', 'customer', 'feedback', 'actions']

    def filter_queryset(self, qs):
        # qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            pass
            qs = qs.filter(Q(email__icontains=sSearch))
        return qs

    
    def render_column(self, row, column):
        # Handle the 'actions' column separately
  

        if column == 'actions':
            return self.render_actions(row)

        elif column == 'feedback':
            # Render a button to view the description
            content_button = f'<button class="btn btn-sm btn-primary view-description" data-row-id="{row.id}">View Feedback</button>'
            content_hidden = f'<div id="descriptionData-{row.id}" style="display: none;">{row.feedback}</div>'
            return content_button + content_hidden
        elif column == 'customer':
            return row.customer.username if row.customer else 'Anonymous user'

        
        return super().render_column(row, column)

    def render_actions(self, row):
        page_id = row.id


        # Delete Button
        delete_url = reverse('store:feedback-list')
        delete_button = f'<a href="{delete_url}?action=delete&pk={row.id}" class="btn btn-sm btn-danger" data-confirm="{_("Are you sure you want to delete this feedback?")}">{_("Delete")}</a>'



        return f'{delete_button}'
    

class ContactQueriesTemplateView(CheckRolesMixin,TemplateView):
    allowed_roles = ('admin',)
    template_name = 'backend/store/contact_queries/contact_queries_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.GET.get('pk')
        contact_query = ContactQueries.objects.filter(pk=pk).first()
        action = self.request.GET.get('action')

        if action == 'delete':
            # Handle delete action
            contact_query.delete() if contact_query else None
            messages.success(self.request, 'Query deleted successfully.')
            # return redirect('store:page-list')
        elif action == 'status':
            contact_query.query_status = ContactQueries.STATUS_CHOICES[0][0] \
                                        if contact_query.query_status == 'Resolved' \
                                        else ContactQueries.STATUS_CHOICES[1][1]
            contact_query.save() if contact_query else None
            messages.success(self.request, 'Query Status updated successfully.')
        elif action == 'send_answer':
            # Handle activate action
            # contact_query.is_active = not page.is_active
            messages.success(self.request, 'Mail Send successfully.')
            # return redirect('store:page-list')
        
        context['answer_query_form'] = AnswerQueryForm()


        return context
    
           


class ContactQueriesDataView(CheckRolesMixin,BaseDatatableView):
    allowed_roles = ('admin',)
    model = ContactQueries
    columns = ['created','id', 'customer__username', 'email', 'query', 'answer', 'actions']

    def filter_queryset(self, qs):
        # qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(email__icontains=sSearch) | Q(customer__username__icontains=sSearch))
        return qs

    def render_column(self, row, column):
        if column == 'actions':
            return self.render_actions(row)
        elif column == 'query':
            # Render a button to view the description
            query_button = f'<button class="btn btn-sm btn-primary view-query" data-row-id="{row.id}">View Query</button>'
            query_hidden = f'<div id="descriptionData-{row.id}" style="display: none;">{row.query}</div>'
            return query_button + query_hidden
        elif column == 'answer':
            answer_button = f'<button class="btn btn-sm btn-primary view-answer" data-row-id="{row.id}">Give Answer</button>'
            answer_hidden = f'<div id="descriptionDataAnswer-{row.id}" style="display: none;">{row.answer}</div>'
            return answer_button + answer_hidden
        return super().render_column(row, column)
    
    def render_actions(self, row):
        query_id = row.id
        current_status = row.query_status

        # Change Query Status Dropdown
        change_status_dropdown = """
            <div class="dropdown">
                <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" id="statusDropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    {0}
                </button>
                <div class="dropdown-menu" aria-labelledby="statusDropdown">
        """.format(current_status)

        # Add options for other available statuses
        for status in ContactQueries.STATUS_CHOICES:
            if status[0] != current_status:
                update_url = reverse('store:contact-queries-list') + f'?action=status&pk={query_id}'
                change_status_dropdown += f'<a class="dropdown-item change-status" data-query-id="{0}" data-status="{1}" href="{update_url}">{ status[1]}</a>'
        change_status_dropdown += """
                </div>
            </div>
        """

        # Send Answer Button
        send_answer_button = f'<button id="send_answer2"  onclick="send_answer({row.id})"class="btn btn-sm btn-success" data-query-id="{query_id}">Send</button>'

        # Delete Query Button
        delete_url = reverse('store:contact-queries-list') + f'?action=delete&pk={query_id}'
        delete_button = f'<a href="{delete_url}" class="btn btn-sm btn-danger" data-confirm="Are you sure you want to delete this query?">Delete</a>'

        # Wrap buttons within a Bootstrap row
        buttons_row = f'<div class="row"> {send_answer_button} {delete_button} {change_status_dropdown}</div>'

        return buttons_row


class HandleContactQueryAnswerView(CheckRolesMixin,View):
    allowed_roles = ('admin',)
    def post(self, request, *args, **kwargs):
        try:
            # Extract data from the POST request
            status = request.POST.get('type')
            content = request.POST.get('content')
            row_id = request.POST.get('rowId')

            # Perform actions based on the status
            if status == 'save':
                # Save the content to your model or perform other actions
                # Example assuming ContactQueries has a field named 'answer':
                instance = get_object_or_404(ContactQueries, id=row_id)
                instance.answer = content
                instance.save()
                return JsonResponse({'status': 'success', 'message': 'Answer saved successfully!'})

            elif status == 'send_now':
                # Perform actions for 'send_now'
                pass
                return JsonResponse({'status': 'success', 'message': 'Answer send successfully!'})
            elif status == 'send_now_noeditor':
                # Perform actions for 'send_now'
                pass
                return JsonResponse({'status': 'success', 'message': 'Answer send successfully!'})
            else:
                pass
                # Handle other status types if needed

            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Action completed successfully'})
        except Exception as e:
            # Return an error response if an exception occurs
            return JsonResponse({'status': 'error', 'message': str(e)})





class CmsSocialsTemplateView(CheckRolesMixin,TemplateView):
    template_name = 'backend/store/socials/manage_socials.html'

    allowed_roles = ('admin',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_socials,created  = CmsSocials.objects.get_or_create(admin=self.request.user)
        context['form'] = CmsSocialsForm(instance=admin_socials)
        return context

    def post(self, request, *args, **kwargs):
        form = CmsSocials.objects.get(admin=self.request.user)
        form = CmsSocialsForm(request.POST, instance=form)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Socials updated successfully.')

            return redirect('store:cms-socials')  # Replace 'socials' with your desired redirect URL
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)
   

class RemoveImageView(CheckRolesMixin,View):
    allowed_roles = ('admin',)
    
    def post(self, request, *args, **kwargs):
        image_id = request.POST.get('image_id')

        try:
            # Assuming ProductImage is your model
            image = ProductImage.objects.filter(id=image_id).first()
            if image:
                image.delete()

            return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
        except ProductImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Image not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)