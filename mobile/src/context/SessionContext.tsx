import React, { createContext, useContext, useMemo, useState } from "react";

interface Session {
  role: "customer" | "staff" | null;
  customerId: string | null;
  name: string | null;
  staffToken: string | null;
  branch: string | null;
}

interface SessionContextValue {
  session: Session;
  logIn: (customerId: string, name: string) => void;
  logInAsStaff: (token: string, name: string, branch?: string) => void;
  logOut: () => void;
}

const EMPTY_SESSION: Session = { role: null, customerId: null, name: null, staffToken: null, branch: null };

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session>(EMPTY_SESSION);

  const value = useMemo<SessionContextValue>(
    () => ({
      session,
      logIn: (customerId: string, name: string) =>
        setSession({ role: "customer", customerId, name, staffToken: null, branch: null }),
      logInAsStaff: (token: string, name: string, branch?: string) =>
        setSession({ role: "staff", customerId: null, name, staffToken: token, branch: branch ?? null }),
      logOut: () => setSession(EMPTY_SESSION),
    }),
    [session]
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within a SessionProvider");
  return ctx;
}
