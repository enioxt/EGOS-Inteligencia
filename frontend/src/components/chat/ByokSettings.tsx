import { useState } from "react";
import { Key, X, ExternalLink, Check, Trash2 } from "lucide-react";
import { getByokKey, setByokKey, hasByokKey } from "@/api/client";

interface ByokSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ByokSettings({ isOpen, onClose }: ByokSettingsProps) {
  const [key, setKey] = useState(() => getByokKey());
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setByokKey(key.trim());
    setSaved(true);
    setTimeout(() => { setSaved(false); onClose(); }, 1200);
  };

  const handleRemove = () => {
    setByokKey("");
    setKey("");
    setSaved(false);
  };

  const hasKey = hasByokKey();

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0,0,0,0.6)",
        backdropFilter: "blur(4px)",
      }}
      onClick={(e: React.MouseEvent<HTMLDivElement>) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        style={{
          background: "#1e293b",
          borderRadius: 12,
          padding: 24,
          width: "90%",
          maxWidth: 440,
          color: "#e2e8f0",
          border: "1px solid #334155",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Key size={20} color="#3b82f6" />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Configurações do Chat</h3>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "#94a3b8", padding: 4 }}>
            <X size={18} />
          </button>
        </div>

        <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.5, margin: "0 0 16px" }}>
          Traga sua própria chave OpenRouter para consultas ilimitadas com os melhores modelos de IA.
          Sua chave fica apenas no seu navegador — nunca é armazenada no servidor.
        </p>

        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 13, fontWeight: 500, display: "block", marginBottom: 6 }}>
            Chave OpenRouter
          </label>
          <input
            type="password"
            value={key}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setKey(e.target.value)}
            placeholder="sk-or-v1-..."
            style={{
              width: "100%",
              padding: "10px 12px",
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: 8,
              color: "#e2e8f0",
              fontSize: 14,
              outline: "none",
              boxSizing: "border-box",
            }}
          />
        </div>

        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          <button
            onClick={handleSave}
            disabled={!key.trim()}
            style={{
              flex: 1,
              padding: "10px 16px",
              background: saved ? "#16a34a" : "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: key.trim() ? "pointer" : "not-allowed",
              fontSize: 14,
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 6,
              opacity: key.trim() ? 1 : 0.5,
            }}
          >
            {saved ? <><Check size={16} /> Salvo!</> : "Salvar chave"}
          </button>
          {hasKey && (
            <button
              onClick={handleRemove}
              style={{
                padding: "10px 12px",
                background: "#1e293b",
                color: "#ef4444",
                border: "1px solid #334155",
                borderRadius: 8,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 4,
                fontSize: 13,
              }}
            >
              <Trash2 size={14} /> Remover
            </button>
          )}
        </div>

        <div style={{
          background: "#0f172a",
          borderRadius: 8,
          padding: 12,
          fontSize: 12,
          color: "#94a3b8",
          lineHeight: 1.6,
        }}>
          <strong style={{ color: "#e2e8f0" }}>Como obter sua chave:</strong>
          <ol style={{ margin: "8px 0 0", paddingLeft: 18 }}>
            <li>
              Crie uma conta grátis em{" "}
              <a
                href="https://openrouter.ai"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#3b82f6", textDecoration: "none" }}
              >
                openrouter.ai <ExternalLink size={10} style={{ display: "inline" }} />
              </a>
            </li>
            <li>Insira créditos (~$5 dura meses com Gemini Flash)</li>
            <li>Vá em Keys → Create Key → cole aqui</li>
          </ol>
          <p style={{ margin: "8px 0 0", fontSize: 11, color: "#64748b" }}>
            🔒 Sua chave fica apenas em localStorage. Sem BYOK, você tem {30} consultas/dia grátis.
          </p>
        </div>
      </div>
    </div>
  );
}
