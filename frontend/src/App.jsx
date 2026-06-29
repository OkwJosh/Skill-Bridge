import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

import SplashPage from './pages/SplashPage';
import OnboardingPage from './pages/OnboardingPage';
import CreateAccountPage from './pages/CreateAccountPage';
import SignInPage from './pages/SignInPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import ChooseRolePage from './pages/ChooseRolePage';
import CreateOrganizationPage from './pages/CreateOrganizationPage';
import CreateSchoolPage from './pages/CreateSchoolPage';
import AboutYouPage from './pages/AboutYouPage';
import AddSkillsPage from './pages/AddSkillsPage';
import SuccessPage from './pages/SuccessPage';
import MyApplicationsPage from './pages/MyApplicationsPage';
import MyMentorsPage from './pages/MyMentorsPage';
import MentorMentorshipsPage from './pages/MentorMentorshipsPage';
import MentorMentorshipDetailPage from './pages/MentorMentorshipDetailPage';
import MentorPostProjectPage from './pages/MentorPostProjectPage';
import OrgProfilePage from './pages/OrgProfilePage';
import OrgOpportunitiesPage from './pages/OrgOpportunitiesPage';
import OrgOpportunityDetailPage from './pages/OrgOpportunityDetailPage';
import SchoolDashboardPage from './pages/SchoolDashboardPage';
import SchoolRosterPage from './pages/SchoolRosterPage';

import AppLayout from './components/AppLayout';
import HomePage from './pages/HomePage';
import JobsPage from './pages/JobsPage';
import JobDetailsPage from './pages/JobDetailsPage';
import TalentPage from './pages/TalentPage';
import TalentProfilePage from './pages/TalentProfilePage';
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage from './pages/SettingsPage';
import ProfilePage from './pages/ProfilePage';
import SearchPage from './pages/SearchPage';
import ApplyPage from './pages/ApplyPage';
import ApplicationSuccessPage from './pages/ApplicationSuccessPage';

function ProtectedRoute({ children }) {
  const { isLoggedIn, loading } = useAuth();
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg)' }}>
      <p style={{ color: 'var(--text-muted)' }}>Loading…</p>
    </div>
  );
  return isLoggedIn ? children : <Navigate to="/sign-in" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SplashPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/create-account" element={<CreateAccountPage />} />
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/choose-role" element={<ChooseRolePage />} />
        <Route path="/create-organization" element={<ProtectedRoute><CreateOrganizationPage /></ProtectedRoute>} />
        <Route path="/create-school" element={<ProtectedRoute><CreateSchoolPage /></ProtectedRoute>} />
        <Route path="/about-you" element={<AboutYouPage />} />
        <Route path="/add-skills" element={<AddSkillsPage />} />
        <Route path="/account-success" element={<SuccessPage />} />

        <Route path="/app" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/app/home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="jobs" element={<JobsPage />} />
          <Route path="jobs/:id" element={<JobDetailsPage />} />
          <Route path="jobs/:id/apply" element={<ApplyPage />} />
          <Route path="jobs/:id/apply/success" element={<ApplicationSuccessPage />} />
          <Route path="my-applications" element={<MyApplicationsPage />} />
          <Route path="my-mentors" element={<MyMentorsPage />} />
          <Route path="talent" element={<TalentPage />} />
          <Route path="talent/:id" element={<TalentProfilePage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />

          {/* Mentor surfaces */}
          <Route path="mentor/mentorships" element={<MentorMentorshipsPage />} />
          <Route path="mentor/mentorships/:id" element={<MentorMentorshipDetailPage />} />
          <Route path="mentor/post-project" element={<MentorPostProjectPage />} />

          {/* Organization surfaces */}
          <Route path="org/profile" element={<OrgProfilePage />} />
          <Route path="org/opportunities" element={<OrgOpportunitiesPage />} />
          <Route path="org/opportunities/:id" element={<OrgOpportunityDetailPage />} />

          {/* School surfaces */}
          <Route path="school" element={<SchoolDashboardPage />} />
          <Route path="school/roster" element={<SchoolRosterPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
