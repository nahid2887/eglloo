# Employee Timer Edit API - Visual Guide

## 🎯 Use Case Scenario

```
Employee Timeline:
─────────────────────────────────────────────────────

Morning:
9:00 AM  - Employee starts working on "Foundation Work"
          Timer is started: START
          
5:00 PM  - Employee stops working
          Timer is stopped: END
          Duration recorded: 8 hours (28800 seconds)

Later that day:
Employee realizes:
- Started at 9:30 AM (not 9:00 AM) - 30 min late clock-in
- Should update the start time

Uses Edit Timer API:
PATCH /api/employee/timer/edit/
{
  "timer_id": 5,
  "start_time": "2025-11-20T09:30:00Z"
}

Result:
- Duration recalculated: 7.5 hours (27000 seconds)
- System shows comparison
- Old: 09:00 to 17:00 = 8 hours
- New: 09:30 to 17:00 = 7.5 hours
```

---

## 📊 Request/Response Flow

```
┌─────────────────────────┐
│  Employee's Browser     │
│                         │
│  Click: "Edit Timer"    │
└────────────┬────────────┘
             │
             │ PATCH Request
             │ Authorization: Bearer TOKEN
             │ {
             │   "timer_id": 5,
             │   "start_time": "2025-11-20T09:30:00Z"
             │ }
             ▼
┌─────────────────────────────────────────┐
│   Django REST API Server                │
│                                         │
│  1. Check Authentication ✓              │
│  2. Check Employee Role ✓               │
│  3. Get Timer (ID: 5) ✓                 │
│  4. Validate Times ✓                    │
│  5. Recalculate Duration ✓              │
│  6. Update Database ✓                   │
│  7. Calculate Daily Total ✓             │
│                                         │
└────────────┬────────────────────────────┘
             │
             │ JSON Response (200 OK)
             │ {
             │   "success": true,
             │   "message": "Timer updated...",
             │   "data": {
             │     "old_values": {...},
             │     "new_values": {...},
             │     "total_time_today": {...}
             │   }
             │ }
             ▼
┌──────────────────────────┐
│  Employee's Browser      │
│                          │
│  Success Message:        │
│  "Timer updated!"        │
│                          │
│  Show Changes:           │
│  Old: 08:00:00          │
│  New: 07:30:00          │
│  Daily Total: 07:30:00  │
└──────────────────────────┘
```

---

## 🔄 Data Transformation

```
Input Data:
──────────
{
  "timer_id": 5,
  "start_time": "2025-11-20T09:30:00Z",
  "end_time": null  // Not provided, will keep existing
}

Processing:
──────────
Step 1: Get existing timer
  Timer #5: 
  - Start: 2025-11-20T09:00:00Z
  - End: 2025-11-20T17:00:00Z
  - Duration: 28800 seconds

Step 2: Update start_time
  Timer #5:
  - Start: 2025-11-20T09:30:00Z  ← UPDATED
  - End: 2025-11-20T17:00:00Z
  - Duration: ? (need to recalc)

Step 3: Recalculate duration
  (09:30) to (17:00) = 7 hours 30 minutes
  = 7.5 hours = 27000 seconds

Output Data:
──────────
{
  "timer": {
    "id": 5,
    "start_time": "2025-11-20T09:30:00Z",
    "end_time": "2025-11-20T17:00:00Z",
    "duration_seconds": 27000
  },
  "old_values": {
    "start_time": "2025-11-20T09:00:00Z",
    "end_time": "2025-11-20T17:00:00Z",
    "duration_seconds": 28800,
    "duration_formatted": "08:00:00"
  },
  "new_values": {
    "start_time": "2025-11-20T09:30:00Z",
    "end_time": "2025-11-20T17:00:00Z",
    "duration_seconds": 27000,
    "duration_formatted": "07:30:00"
  },
  "total_time_today": {
    "seconds": 27000,
    "formatted": "07:30:00"
  }
}
```

---

## 🎬 Common Workflows

### Workflow 1: Fix Late Start Time
```
Scenario: Employee started at 9:30 AM but timer shows 9:00 AM

1. Employee opens app
2. Finds timer for "Foundation Work"
3. Clicks "Edit"
4. Changes Start Time: 09:30
5. Clicks "Save"
6. Duration recalculates from 8h to 7.5h
7. System confirms change
8. Total daily time updates
```

### Workflow 2: Fix Early End Time
```
Scenario: Employee finished at 5:30 PM but timer shows 5:00 PM

1. Employee opens app
2. Finds timer for "Foundation Work"
3. Clicks "Edit"
4. Changes End Time: 17:30
5. Clicks "Save"
6. Duration recalculates from 8h to 8.5h
7. System confirms change
8. Total daily time updates
```

### Workflow 3: Fix Both Times
```
Scenario: Both start and end times are wrong

1. Employee opens app
2. Finds timer for "Foundation Work"
3. Clicks "Edit"
4. Changes Start Time: 09:30
5. Changes End Time: 17:30
6. Clicks "Save"
7. Duration recalculates
8. System confirms both changes
9. Total daily time updates
```

---

## ⏱️ Time Calculation Examples

### Example 1: Standard 8-Hour Day
```
Start:  09:00:00
End:    17:00:00
─────────────────
Diff:   08:00:00
Seconds: 28800
```

### Example 2: Half-Hour Adjustment
```
Start:  09:30:00  (30 min later)
End:    17:00:00  (same)
─────────────────
Diff:   07:30:00  (30 min less)
Seconds: 27000
```

### Example 3: Extra Hour
```
Start:  09:00:00  (same)
End:    18:00:00  (1 hour later)
─────────────────
Diff:   09:00:00  (1 hour more)
Seconds: 32400
```

### Example 4: Crossed Times
```
Start:  10:00:00
End:    16:00:00
─────────────────
Diff:   06:00:00
Seconds: 21600
```

---

## ✅ Validation Checks

```
Request Validation:
───────────────────

┌─ timer_id provided?
│  ├─ NO  → Error: "timer_id is required"
│  └─ YES ↓
│
├─ start_time or end_time provided?
│  ├─ NO  → Error: "At least one time required"
│  └─ YES ↓
│
├─ Valid ISO 8601 datetime format?
│  ├─ NO  → Error: "Invalid datetime format"
│  └─ YES ↓
│
├─ end_time after start_time?
│  ├─ NO  → Error: "End time must be after start"
│  └─ YES ↓
│
├─ Timer exists & belongs to user?
│  ├─ NO  → Error: "Timer not found"
│  └─ YES ↓
│
├─ Timer for past or today?
│  ├─ NO  → Error: "Cannot edit future timers"
│  └─ YES ↓
│
└─ All checks pass!
   ├─ Update timer
   ├─ Recalculate duration
   ├─ Calculate daily total
   └─ Return success (200 OK)
```

---

## 📱 Frontend Implementation Skeleton

```javascript
// Vue.js Component Example
<template>
  <div class="timer-edit-modal">
    <form @submit.prevent="saveChanges">
      <!-- Timer Selection -->
      <select v-model="selectedTimerId">
        <option value="">Select a timer</option>
        <option v-for="timer in timers" :key="timer.id" :value="timer.id">
          {{ timer.task_name }} - {{ timer.work_date }}
        </option>
      </select>

      <!-- Start Time Input -->
      <div class="form-group">
        <label>Start Time</label>
        <input 
          v-model="startTime" 
          type="datetime-local"
          @input="onTimeChange"
        />
        <small>Current: {{ currentStartTime }}</small>
      </div>

      <!-- End Time Input -->
      <div class="form-group">
        <label>End Time</label>
        <input 
          v-model="endTime" 
          type="datetime-local"
          @input="onTimeChange"
        />
        <small>Current: {{ currentEndTime }}</small>
      </div>

      <!-- Duration Preview -->
      <div class="preview">
        <p>Old Duration: {{ oldDuration }}</p>
        <p>New Duration: {{ newDuration }}</p>
      </div>

      <!-- Buttons -->
      <button type="submit" :disabled="!isChanged">Save Changes</button>
      <button type="button" @click="cancel">Cancel</button>
    </form>

    <!-- Result Message -->
    <div v-if="result" :class="['result', result.success ? 'success' : 'error']">
      {{ result.message }}
      <div v-if="result.data" class="details">
        <p>Total today: {{ result.data.total_time_today.formatted }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedTimerId: null,
      startTime: '',
      endTime: '',
      currentStartTime: '',
      currentEndTime: '',
      oldDuration: '',
      newDuration: '',
      result: null,
      timers: [],
      isChanged: false,
    }
  },
  methods: {
    async saveChanges() {
      const response = await fetch('/api/employee/timer/edit/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${this.$store.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          timer_id: this.selectedTimerId,
          start_time: this.startTime ? new Date(this.startTime).toISOString() : undefined,
          end_time: this.endTime ? new Date(this.endTime).toISOString() : undefined,
        })
      });
      
      this.result = await response.json();
      if (this.result.success) {
        this.$emit('updated', this.result.data);
      }
    },
    onTimeChange() {
      this.isChanged = this.startTime !== this.currentStartTime || 
                       this.endTime !== this.currentEndTime;
      this.calculateNewDuration();
    },
    calculateNewDuration() {
      if (this.startTime && this.endTime) {
        const start = new Date(this.startTime);
        const end = new Date(this.endTime);
        const seconds = Math.round((end - start) / 1000);
        this.newDuration = this.formatSeconds(seconds);
      }
    },
    formatSeconds(seconds) {
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = seconds % 60;
      return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    },
    cancel() {
      this.$emit('cancel');
    }
  }
}
</script>
```

---

## 🧪 Testing Matrix

```
TEST CASES:
──────────

┌─ Edit Start Time
│  ├─ Only start time
│  ├─ End time remains
│  ├─ Duration recalculates
│  └─ Daily total updates

├─ Edit End Time
│  ├─ Only end time
│  ├─ Start time remains
│  ├─ Duration recalculates
│  └─ Daily total updates

├─ Edit Both Times
│  ├─ Both changed
│  ├─ Duration recalculates
│  └─ Daily total updates

├─ Validation
│  ├─ Invalid format
│  ├─ End before start
│  ├─ Missing timer_id
│  └─ Future timer

└─ Security
   ├─ Authentication required
   ├─ Own timers only
   ├─ No other users' timers
   └─ No future edits
```

---

## 🔗 Data Model Relationships

```
Employee
  └─ TaskTimer (FK)
      ├─ id
      ├─ employee_id
      ├─ task_id (FK to Task)
      ├─ work_date
      ├─ start_time    ← Can edit
      ├─ end_time      ← Can edit
      ├─ duration_seconds  ← Auto-calculated
      ├─ is_active
      ├─ created_at
      └─ updated_at

Task
  └─ TaskTimer (Reverse FK)
      └─ timers (all timers for this task)

Daily Summary = Sum of all duration_seconds 
                for employee on work_date
```

---

## 📊 Performance Considerations

```
Database Queries:
─────────────────

1. Get Timer (1 query)
   SELECT * FROM emopye_tasktimer WHERE id=5 AND employee_id=X

2. Calculate Daily Total (1 query)
   SELECT SUM(duration_seconds) 
   FROM emopye_tasktimer 
   WHERE employee_id=X AND work_date=2025-11-20

Total: 2 queries per request (optimal)
```

---

## 🎓 DateTime Format Guide

```
ISO 8601 Standard:
──────────────────

Format: YYYY-MM-DDTHH:MM:SSZ

Example: 2025-11-20T09:30:00Z
         ││││││││││││││││││││
         ││││││││││││││││││└─ UTC (Z = +00:00)
         ││││││││││││││││└─── Seconds
         ││││││││││││││└───── Minutes
         ││││││││││││└─────── Hours
         ││││││││││└───────── T (separator)
         ││││││││└─────────── Day
         ││││││└───────────── Month
         └││││─────────────── Year

Timezone Options:
├─ Z        = UTC (+00:00)
├─ +00:00   = UTC
├─ -05:00   = EST (Eastern)
├─ +01:00   = CET (Central Europe)
└─ +09:00   = JST (Japan)

JavaScript:
  const date = new Date('2025-11-20T09:30:00Z');
  const isoString = date.toISOString();
  // Result: "2025-11-20T09:30:00.000Z"

Python:
  from datetime import datetime
  dt = datetime.fromisoformat('2025-11-20T09:30:00+00:00')
  iso_string = dt.isoformat()
```

---

This completes the Employee Timer Edit API! 🎉
