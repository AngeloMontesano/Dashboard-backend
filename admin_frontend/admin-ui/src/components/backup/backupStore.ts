type BackupFile = {
  name: string;
  sizeLabel: string;
  content: string;
};

export type BackupEntry = {
  id: string;
  name: string;
  createdAt: string;
  status: "ok" | "error";
  statusLabel: string;
  files: BackupFile[];
  restoredAt?: string;
};

export type BackupHistoryEntry = {
  id: string;
  backupId: string;
  backupName: string;
  action: "create" | "restore";
  timestamp: string;
  status: "ok" | "error";
  message: string;
};

type BackupState = {
  backups: BackupEntry[];
  history: BackupHistoryEntry[];
};

const STORAGE_KEY = "admin_backup_archive_state";

function nowTimestamp(date = new Date()) {
  return date
    .toISOString()
    .replace("T", " ")
    .replace(/:\d{2}\.\d{3}Z$/, "");
}

function createDemoBackup(index: number): BackupEntry {
  const createdAt = nowTimestamp(new Date(Date.now() - index * 3600_000));
  const id = `backup-${index}`;
  return {
    id,
    name: `tenant-backup-${index}`,
    createdAt,
    status: "ok",
    statusLabel: "OK",
    files: [
      {
        name: "meta.json",
        sizeLabel: "4 KB",
        content: JSON.stringify({ id, createdAt, version: "1.0" }, null, 2),
      },
      {
        name: "tables.json",
        sizeLabel: "18 KB",
        content: JSON.stringify({ tables: ["tenants", "users", "orders"] }, null, 2),
      },
      {
        name: "data.json",
        sizeLabel: "120 KB",
        content: JSON.stringify({ rows: 1240, checksum: "sha256:demo" }, null, 2),
      },
    ],
  };
}

function buildInitialState(): BackupState {
  const backups = [createDemoBackup(1), createDemoBackup(2)];
  const history: BackupHistoryEntry[] = backups.map((backup) => ({
    id: `history-${backup.id}-create`,
    backupId: backup.id,
    backupName: backup.name,
    action: "create",
    timestamp: backup.createdAt,
    status: "ok",
    message: "Backup erstellt",
  }));
  return { backups, history };
}

export function loadBackupState(): BackupState {
  if (typeof window === "undefined") {
    return buildInitialState();
  }
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    const initial = buildInitialState();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
    return initial;
  }
  try {
    const parsed = JSON.parse(raw) as BackupState;
    if (!parsed.backups?.length) {
      const initial = buildInitialState();
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
      return initial;
    }
    return parsed;
  } catch {
    const initial = buildInitialState();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
    return initial;
  }
}

export function saveBackupState(state: BackupState) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function addBackup(state: BackupState): BackupState {
  const nextIndex = state.backups.length + 1;
  const entry = createDemoBackup(nextIndex);
  const historyEntry: BackupHistoryEntry = {
    id: `history-${entry.id}-create`,
    backupId: entry.id,
    backupName: entry.name,
    action: "create",
    timestamp: entry.createdAt,
    status: "ok",
    message: "Backup erstellt",
  };
  const nextState: BackupState = {
    backups: [entry, ...state.backups],
    history: [historyEntry, ...state.history],
  };
  saveBackupState(nextState);
  return nextState;
}

export function markRestore(state: BackupState, backup: BackupEntry): BackupState {
  const timestamp = nowTimestamp();
  const updatedBackups = state.backups.map((entry) =>
    entry.id === backup.id ? { ...entry, restoredAt: timestamp } : entry
  );
  const historyEntry: BackupHistoryEntry = {
    id: `history-${backup.id}-restore-${Date.now()}`,
    backupId: backup.id,
    backupName: backup.name,
    action: "restore",
    timestamp,
    status: "ok",
    message: "Restore abgeschlossen",
  };
  const nextState: BackupState = {
    backups: updatedBackups,
    history: [historyEntry, ...state.history],
  };
  saveBackupState(nextState);
  return nextState;
}
