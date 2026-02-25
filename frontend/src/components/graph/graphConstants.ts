import { dataColors, relationshipColors } from "@/styles/tokens";

export const NODE_COLORS = dataColors;
export const EDGE_COLORS = relationshipColors;

// Node sizes based on connection count
export const NODE_SIZE_MIN = 5;
export const NODE_SIZE_MAX = 14;
export const NODE_SIZE_CENTER = 16;

// LOD thresholds
export const LOD_DOTS_ONLY = 0.5; // zoom < 0.5 = dots only
export const LOD_ICONS = 1.5; // 0.5-1.5 = dots + icon
// > 1.5 = full detail (dots + icon + label + badges)

// Icon map: entity type -> lucide icon name
export const ICON_MAP: Record<string, string> = {
  person: "User",
  company: "Building2",
  election: "Vote",
  contract: "FileText",
  sanction: "AlertTriangle",
  amendment: "FileEdit",
  health: "Heart",
  finance: "DollarSign",
  embargo: "Ban",
  education: "GraduationCap",
  convenio: "Handshake",
  laborstats: "BarChart3",
  pepRecord: "ShieldCheck",
  expulsion: "UserX",
  leniencyAgreement: "Scale",
  internationalSanction: "Globe",
  govCardExpense: "CreditCard",
  govTravel: "Plane",
  bid: "Gavel",
  fund: "PiggyBank",
  douAct: "Newspaper",
  taxWaiver: "Receipt",
  municipalFinance: "Landmark",
  declaredAsset: "Wallet",
  partyMembership: "Users",
  barredNgo: "ShieldOff",
  bcbPenalty: "Banknote",
  laborMovement: "Briefcase",
  legalCase: "Scale",
  cpi: "Search",
};

// Pre-rendered icon cache
const iconCache = new Map<string, HTMLImageElement>();

export function getIconImage(
  type: string,
  color: string,
  size: number,
): HTMLImageElement | null {
  const key = `${type}-${size}`;
  if (iconCache.has(key)) return iconCache.get(key)!;

  const svg = createIconSvg(type, color, size);
  if (!svg) return null;

  const img = new Image();
  img.src = `data:image/svg+xml,${encodeURIComponent(svg)}`;
  iconCache.set(key, img);
  return img;
}

function createIconSvg(type: string, color: string, size: number): string {
  const s = size;
  const shapes: Record<string, string> = {
    person: `<circle cx="${s / 2}" cy="${s * 0.35}" r="${s * 0.2}" fill="${color}"/><ellipse cx="${s / 2}" cy="${s * 0.75}" rx="${s * 0.3}" ry="${s * 0.2}" fill="${color}"/>`,
    company: `<rect x="${s * 0.15}" y="${s * 0.3}" width="${s * 0.7}" height="${s * 0.6}" rx="1" fill="${color}"/><rect x="${s * 0.3}" y="${s * 0.15}" width="${s * 0.4}" height="${s * 0.3}" rx="1" fill="${color}"/>`,
    election: `<rect x="${s * 0.2}" y="${s * 0.2}" width="${s * 0.6}" height="${s * 0.7}" rx="1" fill="${color}"/><polyline points="${s * 0.35},${s * 0.55} ${s * 0.45},${s * 0.65} ${s * 0.65},${s * 0.4}" stroke="#060a07" stroke-width="1.5" fill="none"/>`,
    contract: `<rect x="${s * 0.2}" y="${s * 0.15}" width="${s * 0.6}" height="${s * 0.7}" rx="1" fill="${color}"/><line x1="${s * 0.35}" y1="${s * 0.4}" x2="${s * 0.65}" y2="${s * 0.4}" stroke="#060a07" stroke-width="1"/><line x1="${s * 0.35}" y1="${s * 0.55}" x2="${s * 0.65}" y2="${s * 0.55}" stroke="#060a07" stroke-width="1"/>`,
    sanction: `<polygon points="${s / 2},${s * 0.15} ${s * 0.8},${s * 0.8} ${s * 0.2},${s * 0.8}" fill="${color}"/><text x="${s / 2}" y="${s * 0.7}" text-anchor="middle" font-size="${s * 0.4}" fill="#060a07" font-weight="bold">!</text>`,
    amendment: `<rect x="${s * 0.2}" y="${s * 0.15}" width="${s * 0.6}" height="${s * 0.7}" rx="1" fill="${color}"/><path d="M${s * 0.55} ${s * 0.35} L${s * 0.65} ${s * 0.45} L${s * 0.45} ${s * 0.65} L${s * 0.35} ${s * 0.55} Z" fill="#060a07"/>`,
    health: `<path d="M${s / 2} ${s * 0.25} C${s * 0.35} ${s * 0.15} ${s * 0.15} ${s * 0.25} ${s * 0.15} ${s * 0.4} C${s * 0.15} ${s * 0.6} ${s / 2} ${s * 0.8} ${s / 2} ${s * 0.8} C${s / 2} ${s * 0.8} ${s * 0.85} ${s * 0.6} ${s * 0.85} ${s * 0.4} C${s * 0.85} ${s * 0.25} ${s * 0.65} ${s * 0.15} ${s / 2} ${s * 0.25} Z" fill="${color}"/>`,
    finance: `<rect x="${s * 0.2}" y="${s * 0.2}" width="${s * 0.6}" height="${s * 0.6}" rx="2" fill="${color}"/><text x="${s / 2}" y="${s * 0.6}" text-anchor="middle" font-size="${s * 0.35}" fill="#060a07" font-weight="bold">$</text>`,
    embargo: `<circle cx="${s / 2}" cy="${s / 2}" r="${s * 0.35}" fill="${color}"/><line x1="${s * 0.3}" y1="${s * 0.3}" x2="${s * 0.7}" y2="${s * 0.7}" stroke="#060a07" stroke-width="2"/>`,
    education: `<rect x="${s * 0.15}" y="${s * 0.45}" width="${s * 0.7}" height="${s * 0.35}" rx="1" fill="${color}"/><polygon points="${s / 2},${s * 0.2} ${s * 0.2},${s * 0.45} ${s * 0.8},${s * 0.45}" fill="${color}"/>`,
    convenio: `<circle cx="${s * 0.35}" cy="${s * 0.5}" r="${s * 0.2}" fill="${color}"/><circle cx="${s * 0.65}" cy="${s * 0.5}" r="${s * 0.2}" fill="${color}"/>`,
    laborstats: `<rect x="${s * 0.2}" y="${s * 0.5}" width="${s * 0.15}" height="${s * 0.3}" fill="${color}"/><rect x="${s * 0.425}" y="${s * 0.35}" width="${s * 0.15}" height="${s * 0.45}" fill="${color}"/><rect x="${s * 0.65}" y="${s * 0.2}" width="${s * 0.15}" height="${s * 0.6}" fill="${color}"/>`,
    pepRecord: `<rect x="${s * 0.2}" y="${s * 0.2}" width="${s * 0.6}" height="${s * 0.6}" rx="2" fill="${color}"/><polyline points="${s * 0.35},${s * 0.5} ${s * 0.45},${s * 0.6} ${s * 0.65},${s * 0.35}" stroke="#060a07" stroke-width="1.5" fill="none"/>`,
    expulsion: `<circle cx="${s / 2}" cy="${s * 0.35}" r="${s * 0.2}" fill="${color}"/><line x1="${s * 0.3}" y1="${s * 0.6}" x2="${s * 0.7}" y2="${s * 0.8}" stroke="${color}" stroke-width="2"/><line x1="${s * 0.7}" y1="${s * 0.6}" x2="${s * 0.3}" y2="${s * 0.8}" stroke="${color}" stroke-width="2"/>`,
    leniencyAgreement: `<polygon points="${s / 2},${s * 0.2} ${s * 0.2},${s * 0.6} ${s * 0.8},${s * 0.6}" fill="${color}"/><rect x="${s * 0.35}" y="${s * 0.6}" width="${s * 0.3}" height="${s * 0.2}" fill="${color}"/>`,
    internationalSanction: `<circle cx="${s / 2}" cy="${s / 2}" r="${s * 0.35}" fill="none" stroke="${color}" stroke-width="1.5"/><line x1="${s * 0.15}" y1="${s / 2}" x2="${s * 0.85}" y2="${s / 2}" stroke="${color}" stroke-width="1"/><ellipse cx="${s / 2}" cy="${s / 2}" rx="${s * 0.15}" ry="${s * 0.35}" fill="none" stroke="${color}" stroke-width="1"/>`,
    govCardExpense: `<rect x="${s * 0.15}" y="${s * 0.3}" width="${s * 0.7}" height="${s * 0.45}" rx="2" fill="${color}"/><line x1="${s * 0.15}" y1="${s * 0.45}" x2="${s * 0.85}" y2="${s * 0.45}" stroke="#060a07" stroke-width="1.5"/>`,
    govTravel: `<polygon points="${s / 2},${s * 0.2} ${s * 0.3},${s * 0.5} ${s * 0.7},${s * 0.5}" fill="${color}"/><rect x="${s * 0.35}" y="${s * 0.5}" width="${s * 0.3}" height="${s * 0.25}" fill="${color}"/>`,
    bid: `<rect x="${s * 0.2}" y="${s * 0.2}" width="${s * 0.6}" height="${s * 0.6}" rx="1" fill="${color}"/><text x="${s / 2}" y="${s * 0.6}" text-anchor="middle" font-size="${s * 0.3}" fill="#060a07">§</text>`,
    fund: `<circle cx="${s / 2}" cy="${s * 0.45}" r="${s * 0.3}" fill="${color}"/><rect x="${s * 0.3}" y="${s * 0.15}" width="${s * 0.4}" height="${s * 0.15}" rx="1" fill="${color}"/>`,
    douAct: `<rect x="${s * 0.15}" y="${s * 0.15}" width="${s * 0.7}" height="${s * 0.7}" rx="1" fill="${color}"/><line x1="${s * 0.3}" y1="${s * 0.35}" x2="${s * 0.7}" y2="${s * 0.35}" stroke="#060a07" stroke-width="1"/><line x1="${s * 0.3}" y1="${s * 0.5}" x2="${s * 0.7}" y2="${s * 0.5}" stroke="#060a07" stroke-width="1"/><line x1="${s * 0.3}" y1="${s * 0.65}" x2="${s * 0.55}" y2="${s * 0.65}" stroke="#060a07" stroke-width="1"/>`,
    taxWaiver: `<rect x="${s * 0.2}" y="${s * 0.15}" width="${s * 0.6}" height="${s * 0.7}" rx="1" fill="${color}"/><text x="${s / 2}" y="${s * 0.6}" text-anchor="middle" font-size="${s * 0.3}" fill="#060a07">%</text>`,
    municipalFinance: `<rect x="${s * 0.2}" y="${s * 0.4}" width="${s * 0.6}" height="${s * 0.45}" rx="1" fill="${color}"/><polygon points="${s / 2},${s * 0.15} ${s * 0.15},${s * 0.4} ${s * 0.85},${s * 0.4}" fill="${color}"/>`,
    declaredAsset: `<rect x="${s * 0.15}" y="${s * 0.3}" width="${s * 0.7}" height="${s * 0.45}" rx="3" fill="${color}"/><rect x="${s * 0.25}" y="${s * 0.2}" width="${s * 0.5}" height="${s * 0.15}" rx="2" fill="${color}"/>`,
    partyMembership: `<circle cx="${s * 0.35}" cy="${s * 0.35}" r="${s * 0.18}" fill="${color}"/><circle cx="${s * 0.65}" cy="${s * 0.35}" r="${s * 0.18}" fill="${color}"/><ellipse cx="${s / 2}" cy="${s * 0.72}" rx="${s * 0.35}" ry="${s * 0.18}" fill="${color}"/>`,
    barredNgo: `<rect x="${s * 0.2}" y="${s * 0.2}" width="${s * 0.6}" height="${s * 0.6}" rx="2" fill="${color}"/><line x1="${s * 0.25}" y1="${s * 0.25}" x2="${s * 0.75}" y2="${s * 0.75}" stroke="#060a07" stroke-width="2"/>`,
    bcbPenalty: `<rect x="${s * 0.15}" y="${s * 0.25}" width="${s * 0.7}" height="${s * 0.5}" rx="2" fill="${color}"/><text x="${s / 2}" y="${s * 0.58}" text-anchor="middle" font-size="${s * 0.3}" fill="#060a07" font-weight="bold">B</text>`,
    laborMovement: `<rect x="${s * 0.2}" y="${s * 0.25}" width="${s * 0.6}" height="${s * 0.45}" rx="2" fill="${color}"/><rect x="${s * 0.3}" y="${s * 0.15}" width="${s * 0.4}" height="${s * 0.15}" rx="1" fill="${color}"/>`,
    legalCase: `<polygon points="${s / 2},${s * 0.2} ${s * 0.2},${s * 0.6} ${s * 0.8},${s * 0.6}" fill="${color}"/><rect x="${s * 0.35}" y="${s * 0.6}" width="${s * 0.3}" height="${s * 0.2}" fill="${color}"/>`,
    cpi: `<circle cx="${s / 2}" cy="${s * 0.4}" r="${s * 0.25}" fill="none" stroke="${color}" stroke-width="2"/><line x1="${s * 0.65}" y1="${s * 0.58}" x2="${s * 0.8}" y2="${s * 0.78}" stroke="${color}" stroke-width="2.5"/>`,
  };
  const shape =
    shapes[type] ??
    `<circle cx="${s / 2}" cy="${s / 2}" r="${s * 0.35}" fill="${color}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}" viewBox="0 0 ${s} ${s}">${shape}</svg>`;
}
