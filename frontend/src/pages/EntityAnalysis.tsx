import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router";
import { addJourneyEntry } from "@/lib/journey";

import {
  getEntityByElementId,
  getEntityPatterns,
  getBaseline,
  listInvestigations,
  addEntityToInvestigation,
  createInvestigation,
  type EntityDetail,
  type PatternResponse,
  type BaselineResponse,
  type Investigation,
} from "@/api/client";
import { Spinner } from "@/components/common/Spinner";
import { GraphCanvas } from "@/components/graph/GraphCanvas";
import { ControlsSidebar } from "@/components/graph/ControlsSidebar";
import { AnalysisNav } from "@/components/analysis/AnalysisNav";
import { ConnectionsList } from "@/components/analysis/ConnectionsList";
import { EntityHeader } from "@/components/analysis/EntityHeader";
import { ExportView } from "@/components/analysis/ExportView";
import { InsightsPanel } from "@/components/analysis/InsightsPanel";
import { TimelineView } from "@/components/analysis/TimelineView";
import { useEntityExposure } from "@/hooks/useEntityExposure";
import { useEntityTimeline } from "@/hooks/useEntityTimeline";
import { useGraphData } from "@/hooks/useGraphData";
import { useEntityAnalysisStore } from "@/stores/entityAnalysis";
import { useGraphExplorerStore } from "@/stores/graphExplorer";

import styles from "./EntityAnalysis.module.css";

const RECENT_KEY = "bracc_recent_analyses";
const MAX_RECENT = 10;

interface RecentAnalysis {
  entityId: string;
  name: string;
  type: string;
  exposure: number;
  timestamp: number;
}

function saveRecentAnalysis(entry: RecentAnalysis) {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    const list: RecentAnalysis[] = raw ? (JSON.parse(raw) as RecentAnalysis[]) : [];
    const filtered = list.filter((r) => r.entityId !== entry.entityId);
    filtered.unshift(entry);
    localStorage.setItem(
      RECENT_KEY,
      JSON.stringify(filtered.slice(0, MAX_RECENT)),
    );
  } catch {
    // localStorage unavailable
  }
}

export function EntityAnalysis() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { entityId } = useParams<{ entityId: string }>();
  const id = entityId ?? "";

  // Analysis store
  const {
    activeTab,
    setActiveTab,
    selectedNodeId,
    setSelectedNodeId,
    hoveredNodeId,
    setHoveredNodeId,
    highlightedNodeIds,
  } = useEntityAnalysisStore();

  // Graph explorer store (for graph controls)
  const graphStore = useGraphExplorerStore();

  // Data fetching
  const [entity, setEntity] = useState<EntityDetail | null>(null);
  const [entityLoading, setEntityLoading] = useState(true);
  const [patterns, setPatterns] = useState<PatternResponse | null>(null);
  const [baseline, setBaseline] = useState<BaselineResponse | null>(null);

  // Lazy-load tracking: only fetch heavy data when its section is first viewed
  const loadedSectionsRef = useRef<Set<string>>(new Set());

  const { data: exposure, loading: exposureLoading } = useEntityExposure(id);
  const { data: graphData, loading: graphLoading } = useGraphData(id, graphStore.depth);

  // Timeline: only fetch when timeline tab is activated
  const [timelineEnabled, setTimelineEnabled] = useState(false);
  const {
    events: timelineEvents,
    loading: timelineLoading,
    hasMore: timelineHasMore,
    loadMore: timelineLoadMore,
  } = useEntityTimeline(timelineEnabled ? id : "");

  // Investigation modal
  const [showInvModal, setShowInvModal] = useState(false);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [invLoading, setInvLoading] = useState(false);
  const [newInvTitle, setNewInvTitle] = useState("");

  // Reset lazy-load tracking on entity change
  useEffect(() => {
    loadedSectionsRef.current = new Set();
    setTimelineEnabled(false);
  }, [id]);

  // Trigger lazy loads when tabs are activated
  useEffect(() => {
    if (activeTab === "timeline" && !loadedSectionsRef.current.has("timeline")) {
      loadedSectionsRef.current.add("timeline");
      setTimelineEnabled(true);
    }
  }, [activeTab]);

  // Fetch entity only on mount — patterns and baseline are deferred
  useEffect(() => {
    if (!id) return;
    setEntityLoading(true);

    getEntityByElementId(id)
      .then((ent) => {
        setEntity(ent);
        addJourneyEntry({ type: "entity", title: String(ent.properties?.razao_social || ent.properties?.nome || ent.id || ""), entityId: ent.id, entityType: ent.type || "unknown", url: window.location.pathname });
      })
      .catch(() => {
        // Error handled by component (shows notFound)
      })
      .finally(() => setEntityLoading(false));
  }, [id]);

  // Lazy-load patterns + baseline after entity loads (non-blocking)
  useEffect(() => {
    if (!id || !entity) return;
    if (loadedSectionsRef.current.has("insights")) return;
    loadedSectionsRef.current.add("insights");

    getEntityPatterns(id)
      .then(setPatterns)
      .catch(() => {});
    getBaseline(id)
      .then(setBaseline)
      .catch(() => {});
  }, [id, entity]);

  // Save to recent analyses
  useEffect(() => {
    if (entity && exposure) {
      const rawName =
        entity.properties.nome ??
        entity.properties.razao_social ??
        entity.properties.name ??
        entity.id;
      const name = typeof rawName === "string" ? rawName : String(rawName);
      saveRecentAnalysis({
        entityId: entity.id,
        name,
        type: entity.type,
        exposure: exposure.exposure_index,
        timestamp: Date.now(),
      });
    }
  }, [entity, exposure]);

  // Reset graph store on entity change
  useEffect(() => {
    graphStore.reset();
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Graph data derivatives
  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    if (graphData) {
      for (const node of graphData.nodes) {
        counts[node.type] = (counts[node.type] ?? 0) + 1;
      }
    }
    return counts;
  }, [graphData]);

  const relTypeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    if (graphData) {
      for (const edge of graphData.edges) {
        counts[edge.type] = (counts[edge.type] ?? 0) + 1;
      }
    }
    return counts;
  }, [graphData]);

  // Combine selected + highlighted for graph display
  const graphSelectedIds = useMemo(() => {
    const ids = new Set(highlightedNodeIds);
    if (selectedNodeId) ids.add(selectedNodeId);
    return ids;
  }, [selectedNodeId, highlightedNodeIds]);

  const handleBack = useCallback(() => {
    void navigate(-1);
  }, [navigate]);

  const handleNodeClick = useCallback(
    (nodeId: string) => {
      setSelectedNodeId(nodeId);
      useEntityAnalysisStore.getState().setRightPanelTab("detail");
    },
    [setSelectedNodeId],
  );

  const handleNodeDeselect = useCallback(() => {
    setSelectedNodeId(null);
  }, [setSelectedNodeId]);

  // Investigation modal handlers
  const handleOpenInvModal = useCallback(() => {
    setShowInvModal(true);
    setInvLoading(true);
    listInvestigations()
      .then((res) => setInvestigations(res.investigations))
      .catch(() => {})
      .finally(() => setInvLoading(false));
  }, []);

  const handleAddToInvestigation = useCallback(
    (investigationId: string) => {
      void addEntityToInvestigation(investigationId, id).then(() =>
        setShowInvModal(false),
      );
    },
    [id],
  );

  const handleCreateInvestigation = useCallback(() => {
    if (!newInvTitle.trim()) return;
    void createInvestigation(newInvTitle.trim()).then((inv) => {
      void addEntityToInvestigation(inv.id, id).then(() => {
        setShowInvModal(false);
        setNewInvTitle("");
      });
    });
  }, [newInvTitle, id]);

  // Export stubs
  const handleExportPdf = useCallback(() => {}, []);
  const handleExportCsv = useCallback(() => {}, []);
  const handleExportJson = useCallback(() => {}, []);
  const handleExportScreenshot = useCallback(() => {}, []);

  if (entityLoading) {
    return (
      <div className={styles.loading}>
        <Spinner variant="scan" size="lg" />
      </div>
    );
  }

  if (!entity) {
    return (
      <div className={styles.notFound}>
        <p>{t("analysis.entityNotFound")}</p>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <EntityHeader
        entity={entity}
        exposure={exposure}
        onBack={handleBack}
        onAddToInvestigation={handleOpenInvModal}
      />

      <div className={styles.body}>
        <AnalysisNav activeTab={activeTab} onTabChange={setActiveTab} />

        <main className={styles.center}>
          {activeTab === "graph" && (
            <div className={styles.graphArea}>
              <div className={styles.graphSidebar}>
                <ControlsSidebar
                  collapsed={graphStore.sidebarCollapsed}
                  onToggle={graphStore.toggleSidebar}
                  depth={graphStore.depth}
                  onDepthChange={graphStore.setDepth}
                  enabledTypes={graphStore.enabledTypes}
                  onToggleType={graphStore.toggleType}
                  enabledRelTypes={graphStore.enabledRelTypes}
                  onToggleRelType={graphStore.toggleRelType}
                  typeCounts={typeCounts}
                  relTypeCounts={relTypeCounts}
                />
              </div>
              <div className={styles.graphCanvas}>
                {graphLoading && (
                  <div className={styles.graphOverlay}>
                    <Spinner variant="scan" size="md" />
                  </div>
                )}
                {graphData && (
                  <GraphCanvas
                    data={graphData}
                    centerId={id}
                    enabledTypes={graphStore.enabledTypes}
                    enabledRelTypes={graphStore.enabledRelTypes}
                    hiddenNodeIds={graphStore.hiddenNodeIds}
                    selectedNodeIds={graphSelectedIds}
                    hoveredNodeId={hoveredNodeId}
                    layoutMode={graphStore.layoutMode}
                    onNodeClick={handleNodeClick}
                    onNodeDeselect={handleNodeDeselect}
                    onNodeHover={setHoveredNodeId}
                    onNodeRightClick={() => {}}
                    onLayoutChange={graphStore.setLayoutMode}
                    onFullscreen={graphStore.toggleFullscreen}
                    sidebarCollapsed={graphStore.sidebarCollapsed}
                  />
                )}
              </div>
            </div>
          )}

          {activeTab === "connections" && graphData && (
            <ConnectionsList
              nodes={graphData.nodes}
              centerId={id}
              selectedNodeId={selectedNodeId}
              onSelectNode={handleNodeClick}
            />
          )}

          {activeTab === "timeline" && (
            <TimelineView
              events={timelineEvents}
              loading={timelineLoading}
              hasMore={timelineHasMore}
              onLoadMore={timelineLoadMore}
            />
          )}

          {activeTab === "export" && (
            <ExportView
              onExportPdf={handleExportPdf}
              onExportCsv={handleExportCsv}
              onExportJson={handleExportJson}
              onExportScreenshot={handleExportScreenshot}
            />
          )}
        </main>

        <InsightsPanel
          exposure={exposure}
          patterns={patterns}
          baseline={baseline}
          nodes={graphData?.nodes ?? []}
          exposureLoading={exposureLoading}
        />
      </div>

      {/* Add to Investigation Modal */}
      {showInvModal && (
        <div
          className={styles.overlay}
          onClick={() => setShowInvModal(false)}
          role="presentation"
        >
          <div
            className={styles.modal}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label={t("investigation.addEntity")}
          >
            <h3 className={styles.modalTitle}>
              {t("investigation.addEntity")}
            </h3>

            {invLoading ? (
              <Spinner variant="scan" size="sm" />
            ) : (
              <div className={styles.invList}>
                {investigations.map((inv) => (
                  <button
                    key={inv.id}
                    className={styles.invItem}
                    onClick={() => handleAddToInvestigation(inv.id)}
                  >
                    <span className={styles.invTitle}>{inv.title}</span>
                    <span className={styles.invCount}>
                      {inv.entity_ids.length} {t("investigation.entities")}
                    </span>
                  </button>
                ))}
              </div>
            )}

            <div className={styles.newInv}>
              <input
                type="text"
                value={newInvTitle}
                onChange={(e) => setNewInvTitle(e.target.value)}
                placeholder={t("investigation.newInvestigation")}
                className={styles.newInvInput}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleCreateInvestigation();
                }}
              />
              <button
                className={styles.newInvBtn}
                onClick={handleCreateInvestigation}
                disabled={!newInvTitle.trim()}
              >
                {t("common.confirm")}
              </button>
            </div>

            <button
              className={styles.modalClose}
              onClick={() => setShowInvModal(false)}
            >
              {t("common.cancel")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
