# Timeline Implementation Template

> **For:** All EGOS ecosystem repos
> **Purpose:** Replicable implementation guide
> **Created:** 2026-03-27

---

## Quick Start (1-2 hours per repo)

### Step 1: Copy Components from Forja

```bash
# Copy from forja (reference implementation)
cp forja/src/components/admin/transparency/* YOUR_REPO/src/components/admin/transparency/
cp forja/src/hooks/useRealtimeTelemetry.ts YOUR_REPO/src/hooks/
cp forja/supabase/migrations/20260327*.sql YOUR_REPO/supabase/migrations/
```

### Step 2: Create Admin Page

**File:** `src/app/admin/transparencia/page.tsx`

```typescript
'use client';

import { useState, useCallback } from 'react';
import { TransparencyTimeline, TimelineFilterBar } from '@/components/admin/transparency';
import { useRealtimeTelemetry } from '@/hooks/useRealtimeTelemetry';

export default function TransparencyPage() {
  const { reports, loading, error, refresh } = useRealtimeTelemetry({
    refreshInterval: 30000,
    limit: 50,
  });

  const systems = [...new Set(reports.map(r => r.system))];
  const agents = [...new Set(reports.map(r => r.agent).filter(Boolean))];

  const [filters, setFilters] = useState({});

  const filteredReports = reports.filter(r => {
    if (filters.system && r.system !== filters.system) return false;
    if (filters.agent && r.agent !== filters.agent) return false;
    if (filters.status && r.status !== filters.status) return false;
    if (filters.search && !r.title.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Transparência do Sistema</h1>

      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">
          Erro ao carregar: {error.message}
        </div>
      )}

      <TimelineFilterBar
        onFilter={setFilters}
        systems={systems}
        agents={agents}
      />

      <TransparencyTimeline
        reports={filteredReports}
        loading={loading}
        onRefresh={refresh}
        autoRefresh={true}
        refreshInterval={30000}
      />
    </div>
  );
}
```

### Step 3: Create API Routes

**File:** `src/app/api/admin/transparency/reports/route.ts`

```typescript
import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET(request: NextRequest) {
  try {
    const limit = request.nextUrl.searchParams.get('limit') || '50';

    const { data, error } = await supabase
      .from('transparency_reports')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(parseInt(limit));

    if (error) throw error;

    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const { data, error } = await supabase
      .from('transparency_reports')
      .insert([{
        title: body.title,
        description: body.description,
        system: body.system || 'unknown',
        agent: body.agent,
        status: body.status || 'running',
        triggered_by: body.triggeredBy || 'manual',
        metadata: body.metadata || {},
      }])
      .select();

    if (error) throw error;

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
```

### Step 4: Connect Supabase Client

**Update:** `src/hooks/useRealtimeTelemetry.ts`

```typescript
// Replace the stub with actual Supabase client
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Now the hook will fetch real data
```

### Step 5: Add to Navigation

**Update:** `src/components/layout/AdminNav.tsx` or similar

```typescript
<a href="/admin/transparencia" className="flex items-center gap-2">
  📊 Transparência
</a>
```

### Step 6: Test

```bash
npm run dev
# Visit http://localhost:3000/admin/transparencia
```

---

## Integration Points

### For Each System

#### 852 (Angular/Vite)
- Adapt React components to Angular (using ng-bootstrap)
- Keep API routes same (REST)
- Example: `/admin/telemetry` already exists → extend it

#### Carteira Libre (Next.js/React)
- Straight copy from Forja
- Already has 36 admin pages
- Use as reference implementation

#### egos-lab (Node.js agent runner)
- Emit events to transparency_reports table
- Example: `await emitReport({ title: 'Agent Run', system: 'egos-lab', agent: agentName })`
- No UI needed (headless)

#### br-acc (FastAPI/Neo4j)
- Python client for Supabase
- Emit events from API routes
- Optional dashboard (could use iframe from Forja)

#### smartbuscas (TBD)
- Follow same pattern
- Determine framework first

#### intelink (TBD)
- Likely Angular/Vue
- Adapt components
- Centralized timeline shows ALL investigative events

---

## Customization Points

### Change Refresh Interval
```typescript
refreshInterval={60000}  // 60 seconds instead of 30
```

### Add System-Specific Filters
```typescript
const filteredReports = reports.filter(r => {
  // Custom business logic
  if (mySystem.showOnlyErrors && r.status !== 'failed') return false;
  return true;
});
```

### Customize Component Styling
- Update `statusColors` object in `TransparencyTimeline.tsx`
- Change Tailwind classes to match your design system
- Example: `bg-yellow-100` → `bg-custom-warning`

### Add Custom Columns
```typescript
<TimelineItemCard item={report}>
  <CustomField value={report.metadata.customKey} />
</TimelineItemCard>
```

---

## Troubleshooting

### Data not appearing
1. Check Supabase tables exist: `SELECT * FROM transparency_reports LIMIT 1;`
2. Check RLS policies allow your user: Test with `SELECT` as authenticated user
3. Check API route returns data: `curl http://localhost:3000/api/admin/transparency/reports`

### Auto-refresh not working
1. Check `useRealtimeTelemetry` hook network tab
2. Verify `refreshInterval` > 0
3. Check browser console for errors

### Performance issues
1. Reduce `limit` from 50 to 20
2. Add date filtering (last 24h only)
3. Enable pagination

---

## Timeline for Your Repo

| System | Status | Effort | Start |
|--------|--------|--------|-------|
| Forja | ✅ Components ready | - | Now |
| 852 | 🟡 Extend existing | 6h | Next |
| Carteira Libre | 🟢 Straight copy | 4h | After 852 |
| egos-lab | 🟠 Headless emit | 3h | Parallel |
| br-acc | 🟠 Python SDK | 4h | Parallel |
| smartbuscas | ❓ TBD | TBD | Later |
| intelink | ❓ TBD | TBD | Later |

---

## Support

- **Questions?** Check `TIMELINE_SYSTEM_IMPLEMENTATION_PLAN.md`
- **Forja reference:** `/home/enio/forja/src/components/admin/transparency/`
- **Database schema:** `FORJA/supabase/migrations/20260327120000_transparency_system.sql`
- **Disseminate:** `/disseminate` syncs this guide

---

> **Transparency Principle:**
> "Não seremos uma caixa preta. Iremos mostrando tudo que vamos fazendo."
