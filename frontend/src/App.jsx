import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';

// Auth pages
import SplashPage from './pages/SplashPage';
import OnboardingPage from './pages/OnboardingPage';
import CreateAccountPage from './pages/CreateAccountPage';
import SignInPage from './pages/SignInPage';
import AboutYouPage from './pages/AboutYouPage';
import AddSkillsPage from './pages/AddSkillsPage';
import VerificationPage from './pages/VerificationPage';
import SuccessPage from './pages/SuccessPage';

// App pages (with sidebar layout)
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

export default function App() {
  // Simulate auth state — in real app this would come from backend
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public / Auth flow */}
        <Route path="/" element={<SplashPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/create-account" element={<CreateAccountPage onLogin={() => setIsLoggedIn(true)} />} />
        <Route path="/sign-in" element={<SignInPage onLogin={() => setIsLoggedIn(true)} />} />
        <Route path="/about-you" element={<AboutYouPage />} />
        <Route path="/add-skills" element={<AddSkillsPage />} />
        <Route path="/verification" element={<VerificationPage />} />
        <Route path="/account-success" element={<SuccessPage />} />

        {/* Protected App routes */}
        <Route path="/app" element={<AppLayout />}>
          <Route index element={<Navigate to="/app/home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="jobs" element={<JobsPage />} />
          <Route path="jobs/:id" element={<JobDetailsPage />} />
          <Route path="jobs/:id/apply" element={<ApplyPage />} />
          <Route path="jobs/:id/apply/success" element={<ApplicationSuccessPage />} />
          <Route path="talent" element={<TalentPage />} />
          <Route path="talent/:id" element={<TalentProfilePage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
