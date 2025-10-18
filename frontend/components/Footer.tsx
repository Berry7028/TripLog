export default function Footer() {
  return (
    <footer className="py-4 mt-auto" style={{ backgroundColor: 'var(--footer-deep)', color: '#fff' }}>
      <div className="container mx-auto text-center px-4">
        <p className="mb-1">&copy; 旅ログマップ</p>
        <p className="mb-0">
          <a 
            href="https://maps-planner.vercel.app/" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="text-white underline hover:text-gray-200"
          >
            maps-planner.vercel.app
          </a>
        </p>
      </div>
    </footer>
  );
}
