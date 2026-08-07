"use client";

import { useEffect, useRef, useState } from "react";

import { getAccessToken } from "@/lib/auth";

export type EscalationSocketEventType =
  | "connection.ready"
  | "escalation.created"
  | "escalation.assigned"
  | "escalation.resolved"
  | "pong";

export interface EscalationSocketEvent {
  type: EscalationSocketEventType;

  tenant_id?: string;

  escalation?: {
    id: string;
    tenant_id: string;
    student_id: string;
    reason_code: string;
    status: "open" | "assigned" | "resolved";
    created_at: string;
  };
}

interface UseEscalationSocketOptions {
  tenantId: string;
  onEvent: (event: EscalationSocketEvent) => void;
}

const BASE_RECONNECT_DELAY = 1000;
const MAX_RECONNECT_DELAY = 10000;

export function useEscalationSocket({
  tenantId,
  onEvent,
}: UseEscalationSocketOptions) {
  const [connected, setConnected] = useState(false);

  const callbackRef = useRef(onEvent);

  useEffect(() => {
    callbackRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!tenantId) {
      return;
    }

    const wsBaseUrl =
      process.env.NEXT_PUBLIC_WS_URL ??
      "ws://127.0.0.1:8000";

    let socket: WebSocket | null = null;

    let reconnectTimer:
      | ReturnType<typeof setTimeout>
      | null = null;

    let reconnectAttempts = 0;
    let manuallyClosed = false;

    function connect() {
      // Get the current JWT before every connection/reconnection.
      const token = getAccessToken();

      // If the user is not authenticated, don't open
      // the escalation socket.
      if (!token) {
        setConnected(false);
        return;
      }

      const url = new URL(
        "/ws/escalations",
        wsBaseUrl,
      );

      url.searchParams.set(
        "tenant_id",
        tenantId,
      );

      // Browser WebSockets cannot conveniently send an
      // Authorization header, so send the JWT as a
      // connection query parameter.
      url.searchParams.set(
        "token",
        token,
      );

      socket = new WebSocket(
        url.toString(),
      );

      socket.onopen = () => {
        reconnectAttempts = 0;
        setConnected(true);
      };

      socket.onmessage = (message) => {
        try {
          const event = JSON.parse(
            message.data,
          ) as EscalationSocketEvent;

          callbackRef.current(
            event,
          );
        } catch (error) {
          console.error(
            "Invalid escalation WebSocket message:",
            error,
          );
        }
      };

      socket.onerror = (error) => {
        console.error(
          "Escalation WebSocket error:",
          error,
        );
      };

      socket.onclose = () => {
        setConnected(false);

        if (manuallyClosed) {
          return;
        }

        reconnectAttempts += 1;

        const delay = Math.min(
          BASE_RECONNECT_DELAY *
            2 **
              (reconnectAttempts - 1),
          MAX_RECONNECT_DELAY,
        );

        reconnectTimer = setTimeout(
          connect,
          delay,
        );
      };
    }

    connect();

    const pingTimer = setInterval(
      () => {
        if (
          socket?.readyState ===
          WebSocket.OPEN
        ) {
          socket.send("ping");
        }
      },
      25000,
    );

    return () => {
      manuallyClosed = true;

      setConnected(false);

      clearInterval(
        pingTimer,
      );

      if (reconnectTimer) {
        clearTimeout(
          reconnectTimer,
        );
      }

      socket?.close();
    };
  }, [tenantId]);

  return {
    connected,
  };
}