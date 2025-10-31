# Template Implementation Plans - Literattus Frontend

This document provides detailed structural plans for the 4 missing template pages in the Literattus frontend. Each plan follows the established CSS design system from `frontend/static/css/main.css` and maintains consistency with existing styled pages.

---

## Design System Reference

### Core CSS Classes Available

**Layout & Cards:**
- `.card` - Base card with hover effects and gradient top border
- `.dashboard-card` - Enhanced card for dashboard layouts
- `.dashboard-card-accent` - Card with left accent border (use with `.accent-blue`, `.accent-orange`, `.accent-cyan`)
- `.feature-card` - Card optimized for feature displays
- `.book-card` - Specialized card for book displays

**Buttons:**
- `.btn-primary` - Primary action button (blue gradient)
- `.btn-secondary` - Secondary action button (orange gradient)
- `.btn-outline` - Outlined button

**Forms:**
- `.form-group`, `.form-label`, `.form-input`, `.form-textarea`, `.form-select`

**Hero Sections:**
- `.hero-section` - Full-width hero with gradient background
- `.hero-content`, `.hero-title`, `.hero-subtitle`
- `.hero-geometric`, `.heart`, `.star`, `.moon` - Decorative shapes

**Grids:**
- `.dashboard-grid` - 3-column responsive grid
- `.feature-grid` - Auto-fit grid for features (min 280px)
- `.book-grid` - Grid for book cards (min 200px)

**Animations:**
- `.animate-fade-in` - Fade in effect
- `.animate-slide-left` / `.animate-slide-right` - Slide in effects
- `.animate-float` - Floating animation for decorative elements

**Colors (CSS Variables):**
- `--primary-blue: #1e40af`
- `--accent-orange: #ff6b4a`
- `--accent-cyan: #06b6d4`
- `--accent-gold: #fbbf24`
- `--accent-purple: #a855f7`

---

## 1. Book Detail Page (`books/detail.html`)

### Purpose
Display comprehensive information about a single book with actions for adding to clubs, updating reading progress, and managing the book in the user's catalog.

### URL Pattern
`/books/<int:book_id>/`

### View Context Expected
```python
{
    'title': 'Book Title - Book Details',
    'book': {
        'id': int,
        'title': str,
        'author': str,
        'isbn': str,
        'publisher': str,
        'publishedDate': str,
        'pageCount': int,
        'description': str,
        'coverImage': str (URL),
        'averageRating': float,
        'categories': list[str],
        'language': str
    }
}
```

### Layout Structure

#### 1. Breadcrumb Navigation
```html
<div class="mb-6 text-sm animate-fade-in">
    <a href="{% url 'core:dashboard' %}">Dashboard</a> / 
    <a href="{% url 'books:catalog' %}">My Catalog</a> / 
    <span class="text-gray-600">{{ book.title }}</span>
</div>
```

#### 2. Hero Section (Book Header)
- **CSS Classes:** `.hero-section`, `.hero-content`, `.animate-fade-in`
- **Layout:** Two-column flex layout
  - **Left Column (40%):** Large book cover image
    - Use `.book-cover` styling with shadow effects
    - Fallback placeholder if no cover image
    - Add floating animation (`.animate-float`)
  - **Right Column (60%):** Book metadata
    - Title: Large font (3xl-4xl), gradient text
    - Author: Prominent styling with icon
    - Star rating display (use Font Awesome stars)
    - Publication info badges (year, pages, language)
    - Quick stats grid (rating, pages, published date)

#### 3. Action Buttons Row
- **CSS Classes:** `.btn-primary`, `.btn-secondary`, `.btn-outline`
- **Buttons:**
  - "Update Progress" (primary)
  - "Add to Club" (secondary)
  - "Remove from Catalog" (outline, red accent)
  - "Share" (outline)

#### 4. Tabs Section
```html
<div class="card p-4 mb-8">
    <div class="flex gap-2 border-b border-gray-200 pb-2">
        <button class="px-4 py-2 rounded-t-lg bg-blue-100 text-blue-700 font-semibold">Description</button>
        <button class="px-4 py-2 rounded-t-lg hover:bg-gray-100">Reading Progress</button>
        <button class="px-4 py-2 rounded-t-lg hover:bg-gray-100">Add to Club</button>
    </div>
</div>
```

#### 5. Description Card
- **CSS Classes:** `.card`, `.animate-slide-left`
- Full book description with "Read More" expandable text
- Categories/genres as colored badges
- ISBN and publisher information

#### 6. Reading Progress Card (if in catalog)
- **CSS Classes:** `.dashboard-card`, `.dashboard-card-accent`, `.accent-blue`
- Progress bar showing percentage complete
- Start date and estimated completion
- Form to update current page
- Reading statistics (pages per day, time remaining)

#### 7. Club Selection (for adding book)
- **CSS Classes:** `.dashboard-grid`
- Grid of user's clubs as selectable cards
- Each club shows: name, member count, current book
- "Suggest to Club" button on each card

#### 8. Related Books Section
- **CSS Classes:** `.book-grid`
- Grid of 4-6 related books (same author or genre)
- Each book uses `.book-card` styling
- "Add to Catalog" quick action on hover

### Mobile Responsive Notes
- Stack hero columns vertically on < 768px
- Tabs become dropdown select on mobile
- Related books grid becomes 2 columns on mobile

---

## 2. Club Detail Page (`clubs/club_detail.html`)

### Purpose
Display comprehensive information about a book club including members, current book, discussions, and club activities.

### URL Pattern
`/clubs/<int:club_id>/`

### View Context Expected
```python
{
    'title': 'Club Name - Literattus',
    'club': {
        'id': int,
        'name': str,
        'description': str,
        'createdAt': datetime,
        'memberCount': int,
        'isOwner': bool,
        'isMember': bool,
        'currentBook': {
            'title': str,
            'author': str,
            'coverImage': str,
            'progressPercentage': int
        }
    },
    'members': list[dict],
    'discussions': list[dict],
    'upcomingBooks': list[dict]
}
```

### Layout Structure

#### 1. Hero Header
- **CSS Classes:** `.hero-section`, `.hero-content`
- Gradient background matching club theme
- Club name as `.hero-title`
- Description as `.hero-subtitle`
- Decorative geometric shapes (`.hero-geometric`)
- Floating member count badge

#### 2. Quick Info Cards Row
- **CSS Classes:** `.dashboard-grid`, `.dashboard-card`
- Three cards side-by-side:
  1. **Members Card** (blue accent)
     - Total member count
     - "View All Members" link
     - Member avatars preview (first 5)
  2. **Books Read** (orange accent)
     - Total books completed
     - Current streak
     - "Browse History" link
  3. **Activity** (cyan accent)
     - Discussion count
     - Last activity timestamp
     - "View All" link

#### 3. Current Book Section
- **CSS Classes:** `.card`, `.animate-slide-left`
- Large card featuring current club book
- Two-column layout:
  - **Left:** Book cover (clickable to book detail)
  - **Right:** Book info, collective progress bar, discussion link
- "Start Discussion" button (`.btn-primary`)
- "Vote for Next Book" button (`.btn-secondary`)

#### 4. Members Grid
- **CSS Classes:** `.feature-grid`
- Grid of member cards
- Each card shows:
  - Avatar (circular, gradient fallback)
  - Name and join date
  - Role badge (Owner, Moderator, Member)
  - Reading progress indicator
- Owner/Admin actions (kick, promote) if applicable

#### 5. Discussions List
- **CSS Classes:** `.card`
- List of recent discussions
- Each discussion item:
  - Title, author avatar, comment count
  - Timestamp, last reply preview
  - Hover effect with shadow
- "Create New Discussion" button at top

#### 6. Upcoming Books (Voting)
- **CSS Classes:** `.book-grid`
- Grid of nominated books for next read
- Each book card shows:
  - Cover, title, author
  - Vote count with heart icon
  - "Vote" button
- "Nominate a Book" button

#### 7. Action Buttons (Bottom)
- **Position:** Fixed or sticky bottom bar on mobile
- **Buttons:**
  - "Leave Club" (outline, red) - if member
  - "Join Club" (primary) - if not member
  - "Invite Members" (secondary) - if member
  - "Club Settings" (outline) - if owner

### Mobile Responsive Notes
- Hero title font size reduces to 32px
- Quick info cards stack vertically
- Members grid becomes 2 columns
- Action buttons become full-width sticky footer

---

## 3. My Clubs Page (`clubs/my_clubs.html`)

### Purpose
Display all book clubs the user has joined or created, with filtering and quick actions.

### URL Pattern
`/clubs/my-clubs/`

### View Context Expected
```python
{
    'title': 'My Clubs - Literattus',
    'owned_clubs': list[dict],
    'member_clubs': list[dict],
    'invited_clubs': list[dict],
    'total_count': int
}
```

### Layout Structure

#### 1. Page Header
- **CSS Classes:** `.animate-fade-in`
- Title: "My Book Clubs" (3xl-4xl font, gradient text)
- Subtitle: "Manage your reading communities"
- "Create New Club" button (`.btn-primary`) - right aligned

#### 2. Filter Tabs
- **CSS Classes:** `.card`, `p-4`, `flex`, `gap-2`
- Horizontal tab bar:
  - "All Clubs" (default active)
  - "Owner" - clubs I created
  - "Member" - clubs I joined
  - "Invites" - pending invitations (badge with count)
- Active tab gets blue background (`.bg-blue-100`, `.text-blue-700`)

#### 3. Quick Stats Bar
- **CSS Classes:** `.grid`, `.grid-cols-4`, `.gap-4`, `.mb-8`
- Four stat cards:
  1. Total clubs joined (blue gradient number)
  2. Clubs as owner (orange gradient)
  3. Active discussions (purple gradient)
  4. Books read collectively (green gradient)

#### 4. Clubs Grid
- **CSS Classes:** `.grid`, `.grid-cols-1`, `.md:grid-cols-2`, `.lg:grid-cols-3`, `.gap-6`
- Reuse club card pattern from `club_list.html`
- Each club card includes:
  - **Header:** Gradient banner with club icon/color
  - **Body:**
    - Club name and description
    - Current book title
    - Member count, discussion count
    - Role badge (Owner/Member)
  - **Footer:**
    - "View Club" button (`.btn-outline`)
    - "Quick Actions" dropdown (settings, leave, invite)

#### 5. Empty States (Conditional)
- **If no owned clubs:**
  ```html
  <div class="card p-12 text-center">
      <i class="fas fa-users text-6xl text-blue-300 mb-4"></i>
      <h3>You haven't created any clubs yet</h3>
      <p>Start your own reading community today!</p>
      <button class="btn-primary">Create Your First Club</button>
  </div>
  ```
- **If no member clubs:**
  - Similar pattern with "Browse Clubs" CTA
- **If no invites:**
  - Simple message with "Invite friends" CTA

#### 6. Pending Invites Section (if any)
- **CSS Classes:** `.card`, `.p-6`, `.mb-8`
- List of pending club invitations
- Each invite shows:
  - Club name, inviter name, member preview
  - "Accept" (`.btn-primary`) and "Decline" (`.btn-outline`) buttons
  - Timestamp (invited X days ago)

### Mobile Responsive Notes
- Filter tabs become dropdown select
- Stats grid becomes 2x2 instead of 4x1
- Club cards stack in single column
- Quick action buttons move to card footer

---

## 4. User Profile Page (`auth/profile.html`)

### Purpose
Display user profile information, account settings, reading statistics, and recent activity.

### URL Pattern
`/profile/`

### View Context Expected
```python
{
    'title': 'My Profile - Literattus',
    'user_name': str,
    'user_email': str,
    'username': str,
    'user_id': int,
    'stats': {
        'books_count': int,
        'clubs_count': int,
        'discussions_count': int,
        'reading_streak': int
    }
}
```

### Layout Structure

#### 1. Profile Hero Section
- **CSS Classes:** `.hero-section` (reduced height), `.hero-content`
- Centered layout with:
  - Large avatar (circular, 128px, gradient background with initials)
  - User name below avatar (gradient text)
  - Username (@username) in gray
  - "Edit Profile" button (`.btn-outline`, white border)
  - Floating geometric shapes for decoration

#### 2. Stats Grid
- **CSS Classes:** `.dashboard-grid`
- Four cards with reading statistics:
  1. **Books in Catalog** (blue accent)
     - Large number, "View Catalog" link
  2. **Active Clubs** (orange accent)
     - Club count, "Manage Clubs" link
  3. **Discussions** (cyan accent)
     - Discussion participation count
  4. **Reading Streak** (purple accent)
     - Days in a row, flame icon

#### 3. Profile Information Card
- **CSS Classes:** `.card`, `.p-8`, `.mb-8`
- Two-column layout:
  - **Left Column:**
    - Email address (with verified badge)
    - Username
    - Member since date
    - Account type badge
  - **Right Column:**
    - "Edit Information" button
    - "Change Password" button
    - "Account Settings" button

#### 4. Edit Profile Form (Hidden by Default)
- **CSS Classes:** `.card`, `.p-8`, `.hidden`, `#edit-profile-form`
- Toggle visibility with JavaScript
- **Form Fields:**
  - First Name (`.form-group`, `.form-input`)
  - Last Name
  - Username
  - Email (disabled/read-only)
  - Bio/About (`.form-textarea`)
- **Buttons:**
  - "Save Changes" (`.btn-primary`)
  - "Cancel" (`.btn-outline`)

#### 5. Reading Preferences Card
- **CSS Classes:** `.card`, `.p-6`, `.mb-8`
- Settings for:
  - Favorite genres (multi-select tags)
  - Reading goal (books per year)
  - Notification preferences (toggles)
  - Privacy settings (public/private profile)

#### 6. Recent Activity Timeline
- **CSS Classes:** `.card`, `.p-8`
- Vertical timeline with icons:
  - Book added events (book icon)
  - Club joined events (users icon)
  - Discussion posted events (comment icon)
  - Reading progress milestones (star icon)
- Each item shows:
  - Icon in colored circle (left)
  - Activity description (center)
  - Timestamp (right)

#### 7. Danger Zone Card
- **CSS Classes:** `.card`, `.p-6`, `.border-2`, `.border-red-300`
- Red accent border
- "Delete Account" button with warning
- "Export My Data" button

### Interactive Elements (JavaScript)
```javascript
// Toggle edit profile form
document.getElementById('edit-profile-btn').addEventListener('click', () => {
    document.getElementById('edit-profile-form').classList.toggle('hidden');
});

// Avatar upload preview
document.getElementById('avatar-upload').addEventListener('change', (e) => {
    // Preview uploaded avatar
});
```

### Mobile Responsive Notes
- Profile hero avatar reduces to 96px
- Stats grid becomes 2x2 on mobile
- Two-column layouts stack vertically
- Form fields become full-width

---

## Implementation Notes for All Templates

### Consistent Patterns to Follow

1. **Animation Staggering:**
   - Use `style="animation-delay: Xs;"` where X = 0.1s, 0.2s, 0.3s for sequential cards
   - Apply to `.animate-slide-left`, `.animate-slide-right`, `.animate-fade-in`

2. **Empty States:**
   - Always include empty state designs
   - Use large icons (text-6xl) from Font Awesome
   - Include clear CTA buttons
   - Center align with padding

3. **Loading States:**
   - Consider skeleton loaders for data fetching
   - Use `.animate-pulse` for loading placeholders

4. **Error Handling:**
   - Display Django messages using `.message-alert` classes
   - Show inline validation errors in forms

5. **Accessibility:**
   - Include proper ARIA labels
   - Ensure keyboard navigation works
   - Use semantic HTML5 elements

6. **Backend Integration Points:**
   - All templates should include TODO comments for backend data fetching
   - Example: `<!-- TODO: Fetch from {% url 'api:endpoint' %} -->`
   - Show mock data with clear indicators

7. **Responsive Breakpoints:**
   - Mobile: < 768px
   - Tablet: 768px - 1024px
   - Desktop: > 1024px

### CSS Class Combinations to Use

**For Cards with Accent:**
```html
<div class="dashboard-card dashboard-card-accent accent-blue">
    <!-- Content -->
</div>
```

**For Animated Entry:**
```html
<div class="card animate-slide-left" style="animation-delay: 0.1s;">
    <!-- Content -->
</div>
```

**For Buttons:**
```html
<button class="btn-primary px-6 py-3 rounded-lg font-semibold">
    <i class="fas fa-icon mr-2"></i> Button Text
</button>
```

**For Empty States:**
```html
<div class="card p-12 text-center">
    <div class="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center">
        <i class="fas fa-icon text-5xl text-gray-400"></i>
    </div>
    <h3 class="text-2xl font-bold text-gray-900 mb-3">Title</h3>
    <p class="text-gray-600 mb-6">Description</p>
    <button class="btn-primary">Call to Action</button>
</div>
```

---

## Next Steps for Implementation

1. **Create template files** in appropriate directories
2. **Implement view logic** to fetch data from FastAPI backend
3. **Add URL patterns** to respective `urls.py` files
4. **Test responsive behavior** on multiple screen sizes
5. **Integrate with backend APIs** to replace mock data
6. **Add JavaScript interactions** for dynamic features
7. **Implement form validation** and error handling
8. **Test accessibility** with screen readers and keyboard navigation

---

*Document Version: 1.0*  
*Last Updated: October 30, 2025*  
*Literattus Frontend Development Team*

