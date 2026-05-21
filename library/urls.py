from django.urls import path, include
from library import api_views, views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/loans', api_views.LoanViewSet, basename='loan')

urlpatterns = [
     # ── Dashboard ──────────────────────────────────────────────
    path('',                    views.dashboard,       name='dashboard'),
    
    # ── Books ──────────────────────────────────────────────────
    path('books/',              views.book_list,       name='book_list'),
    path('books/add/',          views.book_add,        name='book_add'),
    path('books/<str:isbn>/',   views.book_detail,     name='book_detail'),
    
    # ── Members ────────────────────────────────────────────────
    path('members/',            views.member_list,     name='member_list'),
    path('members/add/',        views.member_add,      name='member_add'),
    path('members/<str:member_id>/', views.member_detail, name='member_detail'),
    path('members/<str:member_id>/report/', views.member_report, name='member_report'),
    
     # ── Loans ──────────────────────────────────────────────────
    path('borrow/',             views.borrow_book,     name='borrow_book'),
    path('return/',             views.return_book,     name='return_book'),
    
    # ── API endpoints ──────────────────────────────────────────
    path('api/books/',                          api_views.BookListCreateView.as_view(),  name='api_book_list'),
    path('api/books/<str:isbn>/',               api_views.BookDetailView.as_view(),      name='api_book_detail'),
    path('api/members/',                        api_views.MemberListCreateView.as_view(),name='api_member_list'),
    path('api/members/<str:member_id>/',        api_views.MemberDetailView.as_view(),    name='api_member_detail'),
    path('api/loans/borrow/',                   api_views.BorrowBookView.as_view(),      name='api_borrow'),
    path('api/loans/return/',                   api_views.ReturnBookView.as_view(),      name='api_return'),
    path('api/loans/overdue/',                  api_views.OverdueLoansView.as_view(),    name='api_overdue'),
    path('api/reports/summary/',                api_views.LibrarySummaryView.as_view(),  name='api_summary'),
    path('api/members/<str:member_id>/report/', api_views.MemberReportView.as_view(),    name='api_member_report'),
    
    # ── Router (LoanViewSet) ────────────────────────────────────
    path('', include(router.urls)),
]