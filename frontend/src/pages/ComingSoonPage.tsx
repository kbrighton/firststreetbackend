type ComingSoonPageProps = {
  title: string;
  legacyPath: string;
};

export function ComingSoonPage({ title, legacyPath }: ComingSoonPageProps) {
  const baseUrl = (import.meta.env.VITE_LEGACY_BASE_URL || 'http://localhost:5000').replace(/\/$/, '');
  const path = legacyPath.startsWith('/') ? legacyPath : `/${legacyPath}`;

  return (
    <section>
      <h1>{title}</h1>
      <p>This page is not part of the React app yet.</p>
      <a href={`${baseUrl}${path}`}>Open the classic page</a>
    </section>
  );
}
