import React from 'react';

export default function EmailObfuscator({ email, children, className }: EmailObfuscatorProps) {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    // Decode the email and open mail client
    const decodedEmail = atob(email);
    window.location.href = `mailto:${decodedEmail}`;
  };

  return (
    <a
      href="#"
      onClick={handleClick}
      className={className}
      data-email={email}
      rel="nofollow"
    >
      {children}
    </a>
  );
}

// Helper function to encode email for use in components
export const encodeEmail = (email) => {
  return btoa(email);
};

// Usage example:
// <EmailObfuscator email={encodeEmail("info@codeteki.au")}>
//   Contact Us
// </EmailObfuscator>