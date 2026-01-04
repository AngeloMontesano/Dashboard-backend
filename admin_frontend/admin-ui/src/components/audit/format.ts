import type { AuditOut } from "../../types";

export type AuditDisplayRow = AuditOut & {
  actionLabel: string;
  entityLabel: string;
  summary: string;
  createdAtLocal: string;
};

const actionMap: Record<string, string> = {
  create: "Erstellt",
  update: "Geändert",
  delete: "Gelöscht",
};

const entityMap: Record<string, string> = {
  user: "Benutzer",
  tenant: "Kunde",
  tenant_user: "Tenant Benutzer",
};

export function actionLabel(action: string): string {
  return actionMap[action] ?? action;
}

export function entityLabel(entity: string): string {
  return entityMap[entity] ?? entity;
}

function boolText(v: unknown) {
  return v === true ? "ja" : v === false ? "nein" : String(v);
}

export function summarizePayload(payload?: Record<string, unknown> | null): string {
  if (!payload || Object.keys(payload).length === 0) return "Keine Änderungen angegeben";

  const parts: string[] = [];

  if ("email" in payload) parts.push("E-Mail gesetzt");
  if ("name" in payload) parts.push("Name gesetzt");
  if ("slug" in payload) parts.push("Slug gesetzt");
  if ("role" in payload) parts.push(`Rolle: ${payload.role}`);
  if ("tenant_id" in payload) parts.push("Tenant gesetzt");
  if ("user_id" in payload) parts.push("Benutzer gesetzt");
  if ("is_active" in payload) parts.push(`Aktiv: ${boolText(payload.is_active)}`);
  if ("has_password" in payload) parts.push(`Passwort: ${payload.has_password ? "gesetzt" : "nicht gesetzt"}`);
  if ("password" in payload && !("has_password" in payload)) parts.push("Passwort gesetzt");

  const otherKeys = Object.keys(payload).filter(
    (k) => !["email", "name", "slug", "role", "tenant_id", "user_id", "is_active", "has_password", "password"].includes(k)
  );
  otherKeys.forEach((k) => parts.push(`${k} geändert`));

  return parts.length ? parts.join(", ") : "Keine Änderungen angegeben";
}

export function toDisplayRow(row: AuditOut): AuditDisplayRow {
  return {
    ...row,
    actionLabel: actionLabel(row.action),
    entityLabel: entityLabel(row.entity_type),
    summary: summarizePayload(row.payload),
    createdAtLocal: formatLocal(row.created_at),
  };
}

export function formatLocal(iso: string): string {
  try {
    const d = new Date(iso);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
  } catch {
    return iso;
  }
}
