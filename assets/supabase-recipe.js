const SUPABASE_URL = 'https://tsuwporyrjercmuowqyn.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdXdwb3J5cmplcmNtdW93cXluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIzNTMzMDEsImV4cCI6MjA4NzkyOTMwMX0.bKxa62sb5873KegZi5_yMKopablkNJSaw4N6gh3u45Q';

// supabase global is provided by the CDN <script> loaded before this file
const db = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Convert DB row format → instructions.html format and apply to page
function applyRecipeRow(row) {
    if (!row || !row.instructions) return;

    // DB stores [{time, step}], instructions.html expects [[time, text]]
    const instructions = row.instructions.map(i => [i.time ?? null, i.step]);

    // Persist so the page still works on next hard load
    localStorage.setItem('recipe', JSON.stringify({
        dish: row.dish,
        instructions: instructions,
        storageTime: row.storage_time
    }));

    // Live-patch the instructions page if it is currently loaded.
    // steps / currentStep / applyStep / updateButtons are globals defined
    // by the inline <script> in instructions.html (non-module scope, shared).
    if (typeof applyStep === 'function') {
        steps.splice(0, steps.length, ...instructions);
        currentStep = Math.min(currentStep, steps.length - 1);
        applyStep(currentStep, 'up');
        updateButtons();
    }
}

db.channel('recipe-changes')
    .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'recipes' },
        (payload) => {
            console.log('Supabase recipe update:', payload.new);
            applyRecipeRow(payload.new);
        }
    )
    .subscribe((status) => {
        console.log('Supabase channel status:', status);
    });
