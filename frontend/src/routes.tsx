import { Route, Routes } from 'react-router-dom';
import { RequireAdmin } from './auth/RequireAdmin';
import { RequireAuth } from './auth/RequireAuth';
import { AppLayout } from './layout/AppLayout';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { OrderFormPage } from './pages/OrderFormPage';
import { AllDueoutsPage } from './pages/AllDueoutsPage';
import { DueoutsPage } from './pages/DueoutsPage';
import { EditableOrdersPage } from './pages/EditableOrdersPage';
import { SearchLogPage } from './pages/SearchLogPage';
import { SearchPage } from './pages/SearchPage';
import { SearchResultsPage } from './pages/SearchResultsPage';
import { UserFormPage } from './pages/UserFormPage';
import { UsersPage } from './pages/UsersPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route element={<RequireAuth />}>
          <Route path="search" element={<SearchPage />} />
          <Route path="search_log" element={<SearchLogPage />} />
          <Route path="newsearch" element={<EditableOrdersPage />} />
          <Route path="new_search" element={<EditableOrdersPage />} />
          <Route path="order" element={<OrderFormPage />} />
          <Route path="order/:logId" element={<OrderFormPage />} />
          <Route path="order_search" element={<SearchResultsPage />} />
          <Route path="dueouts" element={<DueoutsPage />} />
          <Route path="dueouts_all" element={<AllDueoutsPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="user/:userId/edit" element={<UserFormPage />} />
          <Route element={<RequireAdmin />}>
            <Route path="user/new" element={<UserFormPage />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
