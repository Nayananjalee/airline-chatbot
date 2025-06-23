import Head from 'next/head';
import ChatInterface from '../components/ChatInterface';
import styles from '../styles/Home.module.css';

export default function Home() {
  return (
    <div className={styles.container}>
      <Head>
        <title>Airline Chatbot</title>
        <meta name="description" content="AI-powered airline customer service chatbot" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.header}>
          <h1 className={styles.title}>
            Welcome to <span className={styles.highlight}>Airline Chatbot</span>
          </h1>
          <p className={styles.description}>
            Your AI-powered assistant for flight bookings, travel information, and customer support
          </p>
        </div>
        
        <ChatInterface />
      </main>

      <footer className={styles.footer}>
        <p>Powered by AI - Your trusted travel companion</p>
      </footer>
    </div>
  );
} 