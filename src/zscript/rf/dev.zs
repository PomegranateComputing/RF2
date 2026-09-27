// Development harness. Enabled only through the noarchive cvars rf_dev_tour /
// rf_dev_autopilot. Prints machine-readable RF_DEV_* markers to the console/log.
class RFDevHandler : StaticEventHandler
{
    bool tour;
    bool autopilot;
    bool logging;          // RF_DEV_* console markers (never in normal play)
    Actor apFoe;
    // End-to-end run B: autosave after waypoint rf_dev_save_at; after loading a save, resume at
    // waypoint rf_dev_start_wp; rf_dev_pacifist lets the first life end in death, then the
    // autopilot presses use like a player to resume from the last save. These counters live in
    // the static handler, so they survive the reload.
    int saveAt;
    int startWp;
    bool pacifist;
    int deaths;
    int deadTimer;
    // Opportunistic pickups: ammunition/dressings close to the path, like a player would.
    Inventory apItem;
    int apItemTimer;
    Array<Inventory> apSkip;
    // Door test (rf_dev_doortest): every door line is used from the room it faces, first
    // without keys (locked sides must stay shut), then with both keys.
    bool doortest;
    bool weaponShots;
    // UI capture: rf_dev_ui 1 in a level (HUD under the level title, HUD alone, pause menu; the
    // menu pauses the game, so the last capture and the end marker run on the UI clock);
    // rf_dev_ui 2 on the title screen (main menu, options, credits).
    bool uiShots;
    bool aimShots;          // rf_dev_ui 4: shots at a wall, impacts against the centre dot
    bool soundProbe;        // rf_dev_ui 5: a voice near then far, player shots (distance, centre)
    bool msgShots;          // rf_dev_ui 3: real pickups and a note at the player's feet, captured
    bool deathShots;        // rf_dev_ui 6: the player dies in place; death and resume screen captured
    bool viewShots;         // rf_dev_view "x y z angle pitch; ...": clean views (title art, map evidence)
    Array<double> views;
    int viewIndex, viewTimer;
    // Corpse inspection (rf_dev_corpse): each enemy class killed on flat floor, against a wall,
    // on a door threshold and on a stair; the fall is photographed, then the body from four sides
    // and from above, and its resting state is logged (Z against the floor under it, flags).
    bool corpseTest;
    // Performance (rf_dev_perf): four fixed tour viewpoints held 5 s each; every rendered frame is
    // timed (RenderOverlay) and RF_DEV_PERF gives the frame count, mean and worst frame times.
    bool perfTest;
    bool perfBodies;        // rf_dev_perf 2: twelve bodies killed in view at each scene first
    int perfScene, perfTimer;
    ui int pfScene, pfFrames;
    ui double pfLast, pfSum, pfWorst;
    ui Array<double> pfTimes;
    int cpIndex, cpTimer;
    Actor cpBody;
    // Film (rf_dev_film N): a screenshot every N tics between rf_dev_film_start and _end, each with
    // its millisecond clock, and RF_DEV_SHOT at every player shot, which anchors the game's WAV
    // capture (devrun audio_wav) to the pictures. scripts/film.py assembles the video with sound.
    int filmEvery, filmStart, filmEnd;
    int lastPistol, lastMag;
    ui int uiMenuTics;
    ui int uiTitleTics;
    Array<int> dtLines;
    Array<int> dtSides;
    int dtIndex, dtPhase, dtTimer, dtPass, dtOpen, dtShut;
    double dtBefore;
    Sector dtDoor;
    int ticks;
    Array<Actor> tourPoints;
    Array<Actor> waypoints;
    int tourIndex;
    int tourPhase;
    int tourTimer;
    int apIndex;
    int apTimer;
    int apStuckTimer;
    int apLastHealth;
    int apBacktrackFor;     // waypoint already retried from the previous one (-1: none)
    int apUseCooldown;
    int apTotal;
    Vector2 apLastPos;
    double apBestDist;
    bool apDone;

    static void SortByArg(Array<Actor> list)
    {
        for (int i = 1; i < list.Size(); i++)
        {
            Actor a = list[i];
            int j = i - 1;
            while (j >= 0 && list[j].args[0] > a.args[0]) { list[j + 1] = list[j]; j--; }
            list[j + 1] = a;
        }
    }

    override void WorldLoaded(WorldEvent e)
    {
        ticks = 0;
        tourIndex = 0; tourPhase = 0; tourTimer = 0;
        apIndex = 0; apTimer = 0; apStuckTimer = 0; apUseCooldown = 0; apTotal = 0; apDone = false; apBestDist = 1e9;
        apBacktrackFor = -1;
        tour = CVar.GetCVar('rf_dev_tour').GetBool();
        autopilot = CVar.GetCVar('rf_dev_autopilot').GetBool();
        doortest = CVar.GetCVar('rf_dev_doortest').GetBool();
        weaponShots = CVar.GetCVar('rf_dev_weapons').GetBool() || CVar.GetCVar('rf_dev_art_combat').GetBool();
        uiShots = CVar.GetCVar('rf_dev_ui').GetInt() == 1;
        msgShots = CVar.GetCVar('rf_dev_ui').GetInt() == 3;
        aimShots = CVar.GetCVar('rf_dev_ui').GetInt() == 4;
        soundProbe = CVar.GetCVar('rf_dev_ui').GetInt() == 5;
        deathShots = CVar.GetCVar('rf_dev_ui').GetInt() == 6;
        views.Clear();
        viewIndex = 0; viewTimer = 0;
        String spec = CVar.GetCVar('rf_dev_view').GetString();
        if (spec != "")
        {
            Array<String> items;
            spec.Split(items, ";", TOK_SKIPEMPTY);
            for (int i = 0; i < items.Size(); i++)
            {
                Array<String> v;
                items[i].Split(v, " ", TOK_SKIPEMPTY);
                if (v.Size() < 5) continue;
                for (int j = 0; j < 5; j++) views.Push(v[j].ToDouble());
            }
        }
        viewShots = views.Size() > 0;
        corpseTest = CVar.GetCVar('rf_dev_corpse').GetBool();
        perfTest = CVar.GetCVar('rf_dev_perf').GetInt() > 0;
        perfBodies = CVar.GetCVar('rf_dev_perf').GetInt() == 2;
        perfScene = -1; perfTimer = 0;
        cpIndex = 0; cpTimer = 0; cpBody = null;
        filmEvery = CVar.GetCVar('rf_dev_film').GetInt();
        filmStart = CVar.GetCVar('rf_dev_film_start').GetInt();
        filmEnd = CVar.GetCVar('rf_dev_film_end').GetInt();
        lastPistol = -1;
        lastMag = -1;
        logging = tour || autopilot || doortest || weaponShots || uiShots || corpseTest || perfTest || filmEvery > 0 || deathShots || viewShots || CVar.GetCVar('rf_dev_log').GetBool();
        dtLines.Clear();
        dtSides.Clear();
        dtIndex = 0; dtPhase = 0; dtTimer = 0; dtPass = 0; dtOpen = 0; dtShut = 0;
        if (doortest) CollectDoorLines();
        saveAt = CVar.GetCVar('rf_dev_save_at').GetInt();
        startWp = CVar.GetCVar('rf_dev_start_wp').GetInt();
        pacifist = CVar.GetCVar('rf_dev_pacifist').GetBool();
        deadTimer = 0;
        apItem = null;
        apItemTimer = 0;
        apSkip.Clear();
        tourPoints.Clear();
        waypoints.Clear();
        let it = ThinkerIterator.Create('RFTourPoint');
        Actor a;
        while ((a = Actor(it.Next())) != null)
        {
            if (a is 'RFDevWaypoint') waypoints.Push(a);
            else tourPoints.Push(a);
        }
        SortByArg(tourPoints);
        SortByArg(waypoints);
        int uimode = CVar.GetCVar('rf_dev_ui').GetInt();
        if (uimode == 7 || uimode == 8)
            Console.Printf("RF_DEV_MENU_RESULT map=%s save=%d skill=%d", Level.MapName, e.IsSaveGame, CVar.GetCVar('skill').GetInt());
        if (e.IsSaveGame && startWp > 0) apIndex = clamp(startWp - 1, 0, max(0, waypoints.Size() - 1));
        // After a death the reload may be a later checkpoint autosave: resume from the closest
        // waypoint in sight rather than from rf_dev_start_wp.
        if (e.IsSaveGame && deaths > 0) apIndex = NearestWaypoint(apIndex);
        int monsters = 0, items = 0;
        let all = ThinkerIterator.Create('Actor');
        while ((a = Actor(all.Next())) != null)
        {
            if (a.bIsMonster && a.health > 0) monsters++;
            else if (a is 'Inventory' && Inventory(a).Owner == null) items++;
        }
        if (logging) Console.Printf("RF_DEV_LOADED map=%s save=%d sectors=%d lines=%d monsters=%d items=%d tour=%d waypoints=%d start=%d deaths=%d",
            Level.MapName, e.IsSaveGame, Level.Sectors.Size(), Level.Lines.Size(), monsters, items, tourPoints.Size(), waypoints.Size(),
            apIndex + 1, deaths);
    }

    int NearestWaypoint(int fallback)
    {
        let p = players[consoleplayer].mo;
        if (p == null) return fallback;
        int best = fallback;
        double bestDist = 1e9;
        for (int i = 0; i < waypoints.Size(); i++)
        {
            double d = p.Distance2D(waypoints[i]);
            if (d < bestDist && p.CheckSight(waypoints[i], SF_IGNOREVISIBILITY))
            {
                best = i;
                bestDist = d;
            }
        }
        return best;
    }

    override void WorldUnloaded(WorldEvent e)
    {
        // next= is empty when the level is torn down to load a savegame (death/resume, load menu).
        if (logging) Console.Printf("RF_DEV_UNLOADED map=%s time=%d next=%s", Level.MapName, Level.Time, e.NextMap);
        // Bodies at rest when the level ends (they lay there since their death): height above the
        // floor under them, tilt, and whether they block.
        if (logging && e.NextMap != "")
        {
            let it = ThinkerIterator.Create('RFEnemy');
            RFEnemy en;
            while ((en = RFEnemy(it.Next())) != null)
            {
                if (en.health > 0) continue;
                double under = en.CurSector.floorplane.ZAtPoint(en.Pos.XY);
                Console.Printf("RF_DEV_BODY class=%s x=%.0f y=%.0f dz=%.2f pitch=%.1f roll=%.1f solid=%d vel=%.2f frame=%d",
                    en.GetClassName(), en.Pos.X, en.Pos.Y, en.Pos.Z - under, en.pitch, en.roll, en.bSolid, en.Vel.Length(), en.frame);
            }
        }
    }

    // Aim test: where each bullet lands, as an angle from the player's line of sight (the dot).
    override void WorldThingSpawned(WorldEvent e)
    {
        if (!aimShots || e.Thing == null || !(e.Thing is 'RFBulletPuff')) return;
        let pmo = players[consoleplayer].mo;
        if (pmo == null) return;
        Vector3 d = e.Thing.Pos - (pmo.Pos.X, pmo.Pos.Y, pmo.Pos.Z + PlayerPawn(pmo).ViewHeight);
        double dist = d.XY.Length();
        double yaw = Actor.deltaangle(pmo.angle, atan2(d.Y, d.X));
        double elev = atan2(d.Z, dist);
        Console.Printf("RF_DEV_IMPACT weapon=%s dist=%.0f yaw=%.2f elev=%.2f pitch=%.2f", pmo.player.ReadyWeapon ? pmo.player.ReadyWeapon.GetClassName() : 'none', dist, yaw, elev, -pmo.pitch);
    }

    override void WorldThingDied(WorldEvent e)
    {
        if (!logging || e.Thing == null) return;
        String cls = e.Thing.GetClassName();
        if (e.Thing.player != null)
            Console.Printf("RF_DEV_PLAYER_DIED x=%.0f y=%.0f t=%d", e.Thing.Pos.X, e.Thing.Pos.Y, Level.Time);
        else if (e.Thing.bIsMonster)
            Console.Printf("RF_DEV_DIED class=%s tid=%d x=%.0f y=%.0f t=%d", cls, e.Thing.tid, e.Thing.Pos.X, e.Thing.Pos.Y, Level.Time);
    }

    override void WorldLineActivated(WorldEvent e)
    {
        if (!logging || e.ActivatedLine == null) return;
        let l = e.ActivatedLine;
        Console.Printf("RF_DEV_LINE index=%d special=%d arg0=%d objective=%d t=%d", l.Index(), l.special, l.args[0], l.GetUDMFInt('user_objective'), Level.Time);
    }

    override void WorldTick()
    {
        ticks++;
        if (tour) TourTick();
        if (filmEvery > 0) FilmTick();
        if (msgShots) MessageTick();
        if (aimShots) AimTick();
        if (soundProbe) SoundTick();
        if (corpseTest) CorpseTick();
        if (perfTest) PerfTick();
        if (deathShots) DeathTick();
        if (viewShots) ViewTick();
        if (uiShots)
        {
            if (Level.Time == 60 || Level.Time == 230) Level.MakeScreenShot();
            if (Level.Time == 240) Menu.SetMenu('MainMenu');
        }
    }

    // Spots: corridor centre, corridor north wall, admissions south door strip, west laundry stair.
    // Spots: corridor centre, corridor north wall, admissions south door strip, west laundry stair,
    // beside the admissions counter (40 high) and beside a table (28 high), feet toward them, and
    // the courtyard perron where the E3 porte-registre stands.
    static const double CP_X[] = { -300, -200, 384, 880, 336, 544, 384 };
    static const double CP_Y[] = { -368, -323, -64, 736, -286, -222, 617 };
    static const double CP_A[] = { 0, 180, 90, 0, 270, 270, 270 };

    void CorpseTick()
    {
        let pmo = players[consoleplayer].mo;
        if (pmo == null) return;
        if (Level.Time == 5) Level.ExecuteSpecial(11, null, null, false, 10, 64);   // Door_Open tag 10: the threshold spot
        if (Level.Time < 70) return;
        static const Name kinds[] = { 'RFOrderly', 'RFBrancardier', 'RFPorteRegistre' };
        int total = 3 * 7;
        if (cpIndex >= total)
        {
            if (cpTimer++ == 0) Console.Printf("RF_DEV_CORPSE_DONE");
            return;
        }
        int spot = cpIndex % 7;
        class<Actor> kind = kinds[cpIndex / 7];
        Vector2 at = (CP_X[spot], CP_Y[spot]);
        Sector sec = Level.PointInSector(at);
        double floor = sec.floorplane.ZAtPoint(at);
        if (cpTimer == 0)
        {
            cpBody = Actor.Spawn(kind, (at, floor), ALLOW_REPLACE);
            if (cpBody == null) { cpIndex++; return; }
            cpBody.angle = CP_A[spot];
            // Watch the fall from 128 units in front of the body.
            ViewFrom(pmo, cpBody, CP_A[spot], 128, 0);
        }
        if (cpTimer == 4 && cpBody != null) cpBody.DamageMobj(null, null, 1000, 'None');
        // The fall: frames right after the hit, then the resting pose.
        if (cpTimer == 5 || cpTimer == 11 || cpTimer == 18 || cpTimer == 26 || cpTimer == 40) if (filmEvery == 0) Level.MakeScreenShot();
        if (cpTimer == 60 && cpBody != null)
        {
            double under = cpBody.CurSector.floorplane.ZAtPoint(cpBody.Pos.XY);
            Console.Printf("RF_DEV_CORPSE class=%s spot=%d x=%.0f y=%.0f z=%.2f floorz=%.2f under=%.2f dz=%.2f solid=%d shootable=%d height=%.1f radius=%.1f frame=%d tics=%d vel=%.2f angle=%.1f pitch=%.1f roll=%.1f",
                cpBody.GetClassName(), spot, cpBody.Pos.X, cpBody.Pos.Y, cpBody.Pos.Z, cpBody.floorz, under, cpBody.Pos.Z - cpBody.floorz,
                cpBody.bSolid, cpBody.bShootable, cpBody.Height, cpBody.radius, cpBody.frame, cpBody.tics, cpBody.Vel.Length(), cpBody.angle, cpBody.pitch, cpBody.roll);
        }
        // Around the resting body: four sides at eye level, then from above.
        static const double around[] = { 0, 90, 180, 270 };
        for (int k = 0; k < 4; k++)
        {
            if (cpTimer == 62 + k * 6 && cpBody != null) ViewFrom(pmo, cpBody, CP_A[spot] + around[k], 96, 0);
            if (cpTimer == 65 + k * 6) if (filmEvery == 0) Level.MakeScreenShot();
        }
        if (cpTimer == 86 && cpBody != null) ViewFrom(pmo, cpBody, CP_A[spot] + 45, 40, 1);
        if (cpTimer == 89) if (filmEvery == 0) Level.MakeScreenShot();
        if (++cpTimer > 95)
        {
            if (cpBody != null) cpBody.Destroy();
            cpBody = null;
            cpTimer = 0;
            cpIndex++;
        }
    }

    // Evidence-only stress scene: two waves, all three existing families, existing courtyard.
    // This is not a campaign playthrough or a change to RF01's encounters.
    void ArtCombatTick()
    {
        let p = PlayerPawn(players[consoleplayer].mo);
        if (p == null || p.player == null) return;
        p.player.cheats |= CF_GODMODE;
        p.player.cmd.buttons &= ~(BT_ATTACK | BT_RELOAD | BT_USE);
        if (Level.Time == 10)
        {
            p.SetOrigin((384, 40, 0), false); p.angle = 90; p.pitch = 0;
            p.GiveInventory('RFFAL', 1); p.GiveInventory('RFRifleAmmo', 200);
            p.player.PendingWeapon = Weapon(p.FindInventory('RFFAL'));
        }
        if (Level.Time == 12 || Level.Time == 430)
        {
            static const class<Actor> kinds[] = { 'RFOrderly', 'RFBrancardier', 'RFPorteRegistre', 'RFOrderly', 'RFPorteRegistre' };
            static const double xs[] = { 270, 384, 510, 300, 475 };
            static const double ys[] = { 185, 270, 240, 330, 360 };
            for (int i = 0; i < 5; i++)
            {
                let foe = Actor.Spawn(kinds[i], (xs[i], ys[i], 0));
                if (foe != null) { foe.SetZ(foe.floorz); foe.target = p; foe.angle = 270; foe.SetStateLabel('See'); }
            }
            Console.Printf("RF_ART_STRESS wave_t=%d actors=5 families=3 godmode=1", Level.Time);
        }
        if (Level.Time < 55) return;
        let target = FindFoe(p);
        if (target == null) return;
        Vector2 delta = target.Pos.XY - p.Pos.XY;
        p.angle = atan2(delta.Y, delta.X);
        p.pitch = -atan2(target.Pos.Z + target.Height * 0.55 - p.Pos.Z - p.ViewHeight, max(1.0, delta.Length()));
        let fal = RFFAL(p.FindInventory('RFFAL'));
        if (fal != null && fal.Magazine <= 0) p.player.cmd.buttons |= BT_RELOAD;
        else if ((ticks & 3) == 0) p.player.cmd.buttons |= BT_ATTACK;
    }

    // The view from `dist` units in front of the body along `side`, looking at it; high: from above.
    void ViewFrom(Actor pmo, Actor body, double side, double dist, int high)
    {
        // Stay inside the level: stop 24 units short of the first wall in that direction.
        FLineTraceData hit;
        if (body.LineTrace(side, dist + 24, 0, TRF_THRUACTORS | TRF_NOSKY, 36, 0, 0, hit))
            dist = max(24.0, hit.Distance - 24);
        Vector2 at = body.Pos.XY + (cos(side), sin(side)) * dist;
        Sector sec = Level.PointInSector(at);
        pmo.SetOrigin((at, sec.floorplane.ZAtPoint(at)), false);
        pmo.Vel = (0, 0, 0);
        pmo.angle = side + 180;
        double eye = pmo.Pos.Z + PlayerPawn(pmo).ViewHeight;
        double dz = (body.Pos.Z + 6) - eye;
        pmo.pitch = high ? atan2(eye - body.Pos.Z, dist) : -atan2(dz, dist);
    }

    static const int PERF_POINTS[] = { 1, 5, 9, 13 };

    void PerfTick()
    {
        let pmo = players[consoleplayer].mo;
        if (pmo == null || Level.Time < 70 || tourPoints.Size() < 14) return;
        if (perfTimer == 0)
        {
            perfScene++;
            if (perfScene >= 4)
            {
                if (perfScene == 4) Console.Printf("RF_DEV_PERF_DONE");
                perfScene = 5;
                return;
            }
            Actor pt = tourPoints[PERF_POINTS[perfScene]];
            pmo.SetOrigin((pt.Pos.X, pt.Pos.Y, pt.floorz), false);
            pmo.angle = pt.angle;
            pmo.pitch = pt.args[1];
            pmo.Vel = (0, 0, 0);
            if (pmo.player != null) pmo.player.cheats |= CF_NOCLIP | CF_GODMODE;
            if (perfBodies)
            {
                // Twelve bodies (4 per class) in the view cone, 96-320 units ahead, killed at once.
                static const Name kinds[] = { 'RFOrderly', 'RFBrancardier', 'RFPorteRegistre' };
                int placed = 0;
                for (int i = 0; i < 12; i++)
                {
                    double a = pt.angle + (i % 4 - 1.5) * 12;
                    double d = 96 + (i / 4) * 80;
                    Vector2 at = pt.Pos.XY + (cos(a), sin(a)) * d;
                    FLineTraceData hit;
                    if (pmo.LineTrace(a, d + 32, 0, TRF_THRUACTORS, 24, 0, 0, hit)) continue;
                    Sector sec = Level.PointInSector(at);
                    let mo = Actor.Spawn(kinds[i % 3], (at, sec.floorplane.ZAtPoint(at)), ALLOW_REPLACE);
                    if (mo == null) continue;
                    mo.angle = frandom(0, 360);
                    mo.DamageMobj(null, null, 1000, 'None');
                    placed++;
                }
                Console.Printf("RF_DEV_PERF_BODIES scene=%d placed=%d", perfScene + 1, placed);
            }
        }
        pmo.Vel = (0, 0, 0);
        if (++perfTimer >= 35 * 6) perfTimer = 0;   // 1 s to settle, 5 s measured (UI side)
    }

    // Frame timing: the second after arrival settles, the next five are measured.
    override void RenderOverlay(RenderEvent e)
    {
        if (!perfTest || perfScene < 0) return;
        if (perfScene > 3)
        {
            if (pfScene == 4 && pfFrames > 0) PerfReport();
            pfScene = 5;
            return;
        }
        double now = MSTimeF();
        if (pfScene != perfScene + 1)
        {
            if (pfScene > 0 && pfFrames > 0) PerfReport();
            pfScene = perfScene + 1;
            pfFrames = 0; pfSum = 0; pfWorst = 0; pfLast = now;
            pfTimes.Clear();
            return;
        }
        double dt = now - pfLast;
        pfLast = now;
        if (perfTimer < 35) return;
        pfFrames++;
        pfSum += dt;
        pfWorst = max(pfWorst, dt);
        pfTimes.Push(dt);
    }

    ui void PerfReport()
    {
        int over16 = 0, over33 = 0;
        for (int i = 0; i < pfTimes.Size(); i++)
        {
            if (pfTimes[i] > 16.7) over16++;
            if (pfTimes[i] > 33.3) over33++;
        }
        Console.Printf("RF_DEV_PERF scene=%d point=%d frames=%d mean_ms=%.2f fps=%.1f over16ms=%d over33ms=%d worst_ms=%.2f",
            pfScene, PERF_POINTS[pfScene - 1], pfFrames, pfSum / max(pfFrames, 1), 1000.0 * pfFrames / max(pfSum, 1), over16, over33, pfWorst);
    }

    // Browning then FAL fired straight at the corridor's north wall 96 units away; the impact particles
    // must appear under the centre dot.
    void AimTick()
    {
        let pmo = PlayerPawn(players[consoleplayer].mo);
        if (pmo == null || pmo.player == null) return;
        pmo.player.cheats |= CF_GODMODE;
        pmo.player.cmd.buttons &= ~(BT_ATTACK | BT_USE | BT_RELOAD);
        if (Level.Time == 40)
        {
            pmo.SetOrigin((-300, -400, 0), false);
            pmo.angle = 90; pmo.pitch = 0; pmo.Vel = (0, 0, 0);
            pmo.GiveInventory('RFBrowning', 1);
            pmo.player.PendingWeapon = Weapon(pmo.FindInventory('RFBrowning'));
        }
        if (Level.Time == 80 || Level.Time == 160) probeFire = 2;
        if (Level.Time == 82 || Level.Time == 84 || Level.Time == 162 || Level.Time == 164) Level.MakeScreenShot();
        if (Level.Time == 120)
        {
            pmo.GiveInventory('RFFAL', 1);
            pmo.player.PendingWeapon = Weapon(pmo.FindInventory('RFFAL'));
        }
        if (Level.Time == 180) Console.Printf("RF_DEV_UI_DONE");
    }

    // A sleeping orderly's sight voice at 64 then at 700 units in the corridor, then three player
    // shots; with devrun audio_wav the levels are compared (distance fall-off, centred weapon).
    Actor probeFoe;
    int probeFire;

    // Fire presses of the probes go through the player's think, like the weapon tests: a press
    // made during the level tick does not reach the weapon.
    void DriveProbe(PlayerPawn p)
    {
        if (p.player == null || probeFire <= 0) return;
        p.player.cmd.buttons |= BT_ATTACK;
        probeFire--;
    }
    void SoundTick()
    {
        let pmo = PlayerPawn(players[consoleplayer].mo);
        if (pmo == null || pmo.player == null) return;
        pmo.player.cheats |= CF_GODMODE;
        pmo.player.cmd.buttons &= ~(BT_ATTACK | BT_USE | BT_RELOAD);
        if (Level.Time == 1)
        {
            pmo.A_StartSound("rf/dev/sync", CHAN_AUTO, CHANF_DEFAULT, 1.0, ATTN_NONE);
            Console.Printf("RF_DEV_SYNC t=1 ms=%.1f", MSTimeF());
        }
        if (Level.Time == 30)
        {
            pmo.SetOrigin((-620, -368, 0), false);
            pmo.angle = 0; pmo.pitch = 0; pmo.Vel = (0, 0, 0);
            pmo.GiveInventory('RFBrowning', 1);
            pmo.player.PendingWeapon = Weapon(pmo.FindInventory('RFBrowning'));
        }
        if (Level.Time == 170)
        {
            // The same voice 64 units to the player's left (north): it must pan to the left.
            if (probeFoe != null) probeFoe.Destroy();
            probeFoe = Actor.Spawn('RFOrderly', (-620, -368 + 56, 0));
            if (probeFoe != null)
            {
                probeFoe.bDormant = true;
                probeFoe.A_StartSound("rf/orderly/sight", CHAN_VOICE, CHANF_DEFAULT, 1.0, ATTN_NORM);
                Console.Printf("RF_DEV_SND what=voice_left dist=56 ms=%.1f", MSTimeF());
            }
        }
        if (Level.Time == 70 || Level.Time == 140)
        {
            double d = Level.Time == 70 ? 64 : 700;
            if (probeFoe != null) probeFoe.Destroy();
            probeFoe = Actor.Spawn('RFOrderly', (-620 + d, -368, 0));
            if (probeFoe != null)
            {
                probeFoe.bDormant = true;
                probeFoe.A_StartSound("rf/orderly/sight", CHAN_VOICE, CHANF_DEFAULT, 1.0, ATTN_NORM);
                Console.Printf("RF_DEV_SND what=voice dist=%.0f ms=%.1f", d, MSTimeF());
            }
        }
        if (Level.Time == 210 || Level.Time == 240 || Level.Time == 270)
        {
            probeFire = 2;
            Console.Printf("RF_DEV_SND what=shot dist=0 ms=%.1f", MSTimeF());
        }
        if (Level.Time == 330) Console.Printf("RF_DEV_UI_DONE");
    }

    // Death and resume screen: the player dies where the map starts, the overlay is photographed as it
    // appears and once complete.
    void DeathTick()
    {
        let pmo = players[consoleplayer].mo;
        if (pmo == null) return;
        if (Level.Time == 60) pmo.DamageMobj(null, null, 1000, 'None');
        if (Level.Time == 60 + 50 || Level.Time == 60 + 120) Level.MakeScreenShot();
        if (Level.Time == 60 + 130) Console.Printf("RF_DEV_UI_DONE");
    }

    // Clean views: x y z(above floor) angle pitch per item; noclip and invulnerable, 12 tics to settle.
    void ViewTick()
    {
        let pmo = players[consoleplayer].mo;
        if (pmo == null || Level.Time < 30) return;
        int n = views.Size() / 5;
        if (viewIndex >= n)
        {
            if (viewTimer++ == 0) Console.Printf("RF_DEV_UI_DONE");
            return;
        }
        if (pmo.player != null) pmo.player.cheats |= CF_NOCLIP | CF_GODMODE;
        if (viewTimer == 0)
        {
            Vector2 at = (views[viewIndex * 5], views[viewIndex * 5 + 1]);
            double floor = Level.PointInSector(at).floorplane.ZAtPoint(at);
            pmo.SetOrigin((at, floor + views[viewIndex * 5 + 2]), false);
            pmo.angle = views[viewIndex * 5 + 3];
            pmo.pitch = views[viewIndex * 5 + 4];
        }
        pmo.Vel = (0, 0, 0);
        if (++viewTimer == 12)
        {
            Level.MakeScreenShot();
            Console.Printf("RF_DEV_VIEW index=%d", viewIndex + 1);
        }
        if (viewTimer >= 16) { viewTimer = 0; viewIndex++; }
    }

    void MessageTick()
    {
        let pmo = players[consoleplayer].mo;
        if (pmo == null) return;
        // Touch: the engine's own pickup path (message, sound), as when walking over the item.
        class<Inventory> kind = null;
        if (Level.Time == 180) kind = 'RFPistolAmmo';
        if (Level.Time == 186) kind = 'RFFieldDressing';
        if (Level.Time == 192) kind = 'RFGrilleKey';
        if (kind != null)
        {
            let item = Inventory(Actor.Spawn(kind, pmo.Pos));
            if (item != null) item.Touch(pmo);
        }
        if (Level.Time == 200) pmo.A_Print(StringTable.Localize("$RF_NOTE_3"), 6.0);
        if (Level.Time == 206 || Level.Time == 300 || Level.Time == 420) Level.MakeScreenShot();
        if (Level.Time == 430) Console.Printf("RF_DEV_UI_DONE");
    }

    void FilmTick()
    {
        let pmo = players[consoleplayer].mo;
        if (pmo != null)
        {
            // A shot of the previous tic: the reserve or the magazine went down.
            int pistol = pmo.CountInv('RFPistolAmmo');
            let fal = RFFAL(pmo.FindInventory('RFFAL'));
            int mag = fal != null ? fal.Magazine : -1;
            if ((lastPistol >= 0 && pistol < lastPistol) || (lastMag >= 0 && mag >= 0 && mag < lastMag))
                Console.Printf("RF_DEV_SHOT t=%d ms=%.1f", Level.Time - 1, MSTimeF());
            lastPistol = pistol;
            lastMag = mag;
        }
        if (Level.Time == 1 && pmo != null)
        {
            // Sync tone for the sound track; the filmed span starts later (rf_dev_film_start).
            pmo.A_StartSound("rf/dev/sync", CHAN_AUTO, CHANF_DEFAULT, 1.0, ATTN_NONE);
            Console.Printf("RF_DEV_SYNC t=1 ms=%.1f", MSTimeF());
        }
        if (Level.Time < filmStart || Level.Time > filmEnd) return;
        if ((Level.Time - filmStart) % filmEvery == 0)
        {
            Level.MakeScreenShot();
            Console.Printf("RF_DEV_FILM t=%d ms=%.1f", Level.Time, MSTimeF());
        }
        if (Level.Time == filmEnd) Console.Printf("RF_DEV_FILM_DONE");
    }

    override void UiTick()
    {
        int uimode = CVar.FindCVar('rf_dev_ui').GetInt();
        if (uimode == 2)
        {
            TitleMenuShots();      // counts from engine start, whatever plays behind the title
            return;
        }
        if (uimode == 7 || uimode == 8)
        {
            MenuDrive(uimode);
            return;
        }
        if (!uiShots || Level.Time < 240) return;
        // Pause, then the save list and the "main menu" confirmation opened from it.
        uiMenuTics++;
        if (uiMenuTics == 20) Level.MakeScreenShot();
        if (uiMenuTics == 25) Menu.SetMenu('SaveGameMenu');
        if (uiMenuTics == 45) Level.MakeScreenShot();
        if (uiMenuTics == 50) Menu.SetMenu('EndGameMenu');
        if (uiMenuTics == 70) Level.MakeScreenShot();
        if (uiMenuTics == 75) Console.Printf("RF_DEV_UI_DONE");
    }

    // Menu navigation through the menus' own input handling, from the title screen: 7 = "Continuer" (the
    // newest save), 8 = "Nouvelle partie" then the preselected difficulty. The level that loads reports
    // RF_DEV_MENU_RESULT (WorldLoaded).
    ui void MenuDrive(int mode)
    {
        uiTitleTics++;
        if (uiTitleTics == 175) Menu.SetMenu('MainMenu');
        let m = Menu.GetCurrentMenu();
        if (m == null) return;
        if (mode == 7 && uiTitleTics == 200) { Level.MakeScreenShot(); m.MenuEvent(Menu.MKEY_Enter, false); }
        if (mode == 8)
        {
            let main = RFMainMenu(m);
            if (uiTitleTics == 200 && main != null) { main.sel = 1; Level.MakeScreenShot(); m.MenuEvent(Menu.MKEY_Enter, false); }
            if (uiTitleTics == 230) { Level.MakeScreenShot(); m.MenuEvent(Menu.MKEY_Enter, false); }
        }
    }

    ui void TitleMenuShots()
    {
        // The engine's intro logo plays first: menus open after 5 s. RF2-UI-01: every title-side screen,
        // each opened over the previous one like a player would (main, difficulty, load, options,
        // credits, quit confirmation).
        uiTitleTics++;
        static const Name menus[] = { 'MainMenu', 'SkillMenu', 'LoadGameMenu', 'RFOptionsMenu', 'RFCreditsMenu', 'QuitMenu' };
        int k = (uiTitleTics - 175) / 25;
        int phase = (uiTitleTics - 175) % 25;
        if (uiTitleTics < 175) return;
        if (k < 6 && phase == 0) Menu.SetMenu(menus[k]);
        if (k < 6 && phase == 20) Level.MakeScreenShot();
        if (k == 6 && phase == 5) Console.Printf("RF_DEV_UI_DONE");
    }

    void TourTick()
    {
        if (!playeringame[0] || players[0].mo == null) return;
        if (tourPoints.Size() == 0)
        {
            if (ticks == 30) Level.MakeScreenShot();
            if (ticks == 45) Console.Printf("RF_DEV_TOUR_DONE shots=1");
            return;
        }
        if (ticks < 30) return;
        Actor p = players[0].mo;
        if (tourPhase == 0)
        {
            if (tourIndex >= tourPoints.Size())
            {
                tourPhase = 3;
                Console.Printf("RF_DEV_TOUR_DONE shots=%d", tourPoints.Size());
                return;
            }
            Actor pt = tourPoints[tourIndex];
            p.SetOrigin((pt.Pos.X, pt.Pos.Y, pt.floorz), false);
            p.angle = pt.angle;
            p.pitch = pt.args[1];
            p.Vel = (0, 0, 0);
            if (p.player != null) { p.player.cheats |= CF_NOCLIP | CF_GODMODE; }
            tourTimer = 0;
            tourPhase = 1;
        }
        else if (tourPhase == 1)
        {
            if (++tourTimer >= 10)
            {
                Level.MakeScreenShot();
                Console.Printf("RF_DEV_SHOT index=%d x=%.0f y=%.0f", tourPoints[tourIndex].args[0], p.Pos.X, p.Pos.Y);
                tourTimer = 0;
                tourPhase = 2;
            }
        }
        else if (tourPhase == 2)
        {
            if (++tourTimer >= 8) { tourIndex++; tourPhase = 0; }
        }
    }

    Actor FindFoe(Actor p)
    {
        Actor best = null;
        double bestDist = 900;
        let it = ThinkerIterator.Create('Actor');
        Actor a;
        while ((a = Actor(it.Next())) != null)
        {
            if (!a.bIsMonster || a.health <= 0 || a.bDormant) continue;
            double d = p.Distance2D(a);
            if (d < bestDist && p.CheckSight(a)) { best = a; bestDist = d; }
        }
        return best;
    }

    // Weapon capture (rf_dev_weapons): FAL fire with its flash layer and the empty-magazine
    // reload, screenshotted in the engine at fixed tics (the promoted Astra frames seen in game).
    void DriveWeaponShots(PlayerPawn p)
    {
        if (CVar.GetCVar('rf_dev_art_combat').GetBool()) { ArtCombatTick(); return; }
        if (p.player == null) return;
        p.player.cheats |= CF_GODMODE;
        p.player.cmd.forwardmove = 0;
        p.player.cmd.sidemove = 0;
        p.player.cmd.buttons &= ~(BT_ATTACK | BT_USE | BT_RELOAD);
        if (ticks == 10)
        {
            p.GiveInventory('RFBrowning', 1);
            p.player.PendingWeapon = Weapon(p.FindInventory('RFBrowning'));
            // The three families side by side in the courtyard, idle, ~200 units away: scale, ground contact.
            p.SetOrigin((384, 40, p.floorz), false);
            p.angle = 90;
            p.pitch = 0;
            static const class<Actor> lineup[] = { 'RFOrderly', 'RFBrancardier', 'RFPorteRegistre' };
            static const double lineupX[] = { 290, 384, 480 };
            for (int i = 0; i < 3; i++)
            {
                let mo = Actor.Spawn(lineup[i], (lineupX[i], 240, 0));
                if (mo != null) { mo.angle = 270; mo.bDormant = true; mo.SetZ(mo.floorz); }
            }
        }
        if (ticks == 32) if (filmEvery == 0) Level.MakeScreenShot();
        if (ticks == 35) p.player.cmd.buttons |= BT_ATTACK;
        if (ticks == 36 || ticks == 39 || ticks == 45) if (filmEvery == 0) Level.MakeScreenShot();
        if (ticks == 50)
        {
            p.SetOrigin((384, -500, 0), false);
            p.angle = 90;
            p.pitch = 0;
            p.GiveInventory('RFFAL', 1);
            p.player.PendingWeapon = Weapon(p.FindInventory('RFFAL'));
        }
        let fal = RFFAL(p.FindInventory('RFFAL'));
        if (fal == null) return;
        if (ticks == 110) p.player.cmd.buttons |= BT_ATTACK;
        if (ticks == 111 || ticks == 113) if (filmEvery == 0) Level.MakeScreenShot();        // FIRE + flash, RECOIL
        if (ticks == 150) fal.Magazine = 0;
        if (ticks == 152) p.player.cmd.buttons |= BT_RELOAD;
        if (ticks > 152 && ticks <= 212 && (ticks - 152) % 8 == 0) if (filmEvery == 0) Level.MakeScreenShot();   // reload poses
        if (ticks == 230) if (filmEvery == 0) Level.MakeScreenShot();                        // ready again
        if (ticks == 240) Console.Printf("RF_ART_EMPTY_RELOAD mag=%d reserve=%d", fal.Magazine, fal.ReserveCount());
        if (ticks == 245) { fal.Magazine = 10; p.GiveInventory('RFRifleAmmo', 20); }
        if (ticks == 247) p.player.cmd.buttons |= BT_RELOAD;
        if (ticks == 310) { if (filmEvery == 0) Level.MakeScreenShot(); Console.Printf("RF_ART_PARTIAL_RELOAD mag=%d reserve=%d", fal.Magazine, fal.ReserveCount()); }
        if (ticks == 325) p.player.PendingWeapon = Weapon(p.FindInventory('RFBrowning'));
        if (ticks == 360) p.TakeInventory('RFPistolAmmo', 999);
        if (ticks == 370) if (filmEvery == 0) Level.MakeScreenShot();
        if (ticks == 375) p.player.cmd.buttons |= BT_ATTACK;
        if (ticks == 385) if (filmEvery == 0) Level.MakeScreenShot();
        if (ticks == 420) Console.Printf("RF_DEV_WEAPONS_DONE mag=%d reserve=%d pistol=%d", fal.Magazine, fal.ReserveCount(), p.CountInv('RFPistolAmmo'));
    }

    // Door lines bounding a closed door sector, with the side of the room they face.
    void CollectDoorLines()
    {
        for (int i = 0; i < Level.Lines.Size(); i++)
        {
            Line l = Level.Lines[i];
            if ((l.special != 11 && l.special != 12 && l.special != 13) || l.backsector == null) continue;
            if (l.frontsector == l.backsector || !(l.activation & SPAC_Use)) continue;
            double hf = l.frontsector.CenterCeiling() - l.frontsector.CenterFloor();
            double hb = l.backsector.CenterCeiling() - l.backsector.CenterFloor();
            if (min(hf, hb) >= 56) continue;
            dtLines.Push(i);
            dtSides.Push(hf < hb ? Line.back : Line.front);
        }
    }

    // One use per door line from its room side; reports open/shut after 80 tics.
    void DriveDoorTest(PlayerPawn p)
    {
        if (p.player == null) return;
        p.player.cheats |= CF_GODMODE;
        p.player.cmd.forwardmove = 0;
        p.player.cmd.sidemove = 0;
        p.player.cmd.buttons &= ~(BT_ATTACK | BT_USE);
        if (dtPass > 1 || ticks < 20) return;
        if (dtIndex >= dtLines.Size())
        {
            Console.Printf("RF_DEV_DOORTEST_PASS pass=%d lines=%d open=%d shut=%d", dtPass + 1, dtLines.Size(), dtOpen, dtShut);
            dtPass++;
            dtIndex = 0; dtPhase = 0; dtOpen = 0; dtShut = 0;
            if (dtPass == 1) { p.GiveInventory('RFGrilleKey', 1); p.GiveInventory('RFPasseKey', 1); }
            if (dtPass > 1) Console.Printf("RF_DEV_DOORTEST_DONE");
            return;
        }
        Line l = Level.Lines[dtLines[dtIndex]];
        int side = dtSides[dtIndex];
        Sector room = side == Line.front ? l.frontsector : l.backsector;
        dtDoor = side == Line.front ? l.backsector : l.frontsector;
        if (dtPhase == 0)
        {
            // A door still open from the other side's test would give a false "open": wait for it.
            double hNow = dtDoor.CenterCeiling() - dtDoor.CenterFloor();
            if (hNow > 8 && ++dtTimer < 260) return;
            Vector2 a = l.v1.p, b = l.v2.p;
            Vector2 dir = (b - a).Unit();
            Vector2 right = (dir.Y, -dir.X);                 // front side of the line
            Vector2 n = side == Line.front ? right : -right;
            Vector2 stand = (a + b) / 2 + n * 36;
            p.SetOrigin((stand.X, stand.Y, room.floorplane.ZAtPoint(stand)), false);
            p.Vel = (0, 0, 0);
            p.angle = atan2(-n.Y, -n.X);
            p.pitch = 0;
            dtTimer = 0;
            dtPhase = 1;
        }
        else if (dtPhase == 1)
        {
            if (dtTimer == 0) dtBefore = dtDoor.CenterCeiling() - dtDoor.CenterFloor();
            if (++dtTimer == 6) p.player.cmd.buttons |= BT_USE;
            if (dtTimer >= 86)
            {
                double h = dtDoor.CenterCeiling() - dtDoor.CenterFloor();
                bool open = h >= 56;
                // A Door_Open door opened earlier never closes: this side cannot be judged again.
                String result = dtBefore >= 56 ? "was_open" : open ? "open" : "shut";
                if (open) dtOpen++; else dtShut++;
                Console.Printf("RF_DEV_DOOR pass=%d line=%d special=%d tag=%d lock=%d result=%s h=%.0f",
                    dtPass + 1, l.Index(), l.special, l.args[0], l.special == 13 ? l.args[3] : 0, result, h);
                dtIndex++;
                dtPhase = 0;
                dtTimer = 0;
            }
        }
    }

    // Nearest useful ammunition or dressing within reach of the path, on the player's level.
    Inventory FindPickup(PlayerPawn p)
    {
        Inventory best = null;
        double bestDist = 112;
        let it = ThinkerIterator.Create('Inventory');
        Inventory inv;
        while ((inv = Inventory(it.Next())) != null)
        {
            if (inv.Owner != null || !(inv is 'Ammo' || inv is 'Health')) continue;
            if (apSkip.Find(inv) != apSkip.Size() || abs(inv.Pos.Z - p.Pos.Z) > 40) continue;
            if (inv is 'Health' && p.health >= 90) continue;
            if (inv is 'Ammo')
            {
                let held = p.FindInventory(inv.GetClass());
                if (held != null && held.Amount >= held.MaxAmount) continue;
            }
            double d = p.Distance2D(inv);
            if (d < bestDist && p.CheckSight(inv)) { best = inv; bestDist = d; }
        }
        return best;
    }

    String AmmoState(PlayerPawn p)
    {
        let fal = RFFAL(p.FindInventory('RFFAL'));
        String wpn = p.player.ReadyWeapon != null ? p.player.ReadyWeapon.GetClassName() : 'none';
        return String.Format("wpn=%s mag=%d res=%d p9=%d", wpn, fal != null ? fal.Magazine : -1,
            fal != null ? fal.ReserveCount() : -1, p.CountInv('RFPistolAmmo'));
    }

    // The FAL while it has rounds (magazine or reserve), else the Browning.
    Weapon FightWeapon(PlayerPawn p)
    {
        let fal = RFFAL(p.FindInventory('RFFAL'));
        if (fal != null && (fal.Magazine > 0 || fal.ReserveCount() > 0)) return fal;
        let pistol = Weapon(p.FindInventory('RFBrowning'));
        if (pistol != null && p.CountInv('RFPistolAmmo') > 0) return pistol;
        return fal != null ? Weapon(fal) : pistol;
    }

    // True when the door line the player faces belongs to a door that is already open:
    // pressing use there would close a Door_Raise again, so the autopilot must not.
    bool DoorAheadOpen(PlayerPawn p)
    {
        let it = BlockLinesIterator.Create(p, 96);
        Vector2 fwd = (cos(p.angle), sin(p.angle));
        while (it.Next())
        {
            Line l = it.CurLine;
            if ((l.special != 12 && l.special != 13) || l.frontsector == null || l.backsector == null) continue;
            Vector2 mid = (l.v1.p + l.v2.p) / 2;
            Vector2 d = mid - p.Pos.XY;
            double len = d.Length();
            if (len > 90 || len < 1 || (d.X * fwd.X + d.Y * fwd.Y) < len * 0.6) continue;
            double hf = l.frontsector.CenterCeiling() - l.frontsector.CenterFloor();
            double hb = l.backsector.CenterCeiling() - l.backsector.CenterFloor();
            return min(hf, hb) >= 60;
        }
        return false;
    }

    // Steers the player through RFDevWaypoint markers using ordinary input.
    void DriveAutopilot(PlayerPawn p)
    {
        if (p.player == null) return;
        if (p.health <= 0)
        {
            p.player.cmd.buttons &= ~(BT_ATTACK | BT_USE);
            if (deadTimer++ == 0)
            {
                deaths++;
                Console.Printf("RF_DEV_AUTOPILOT_DEATH n=%d waypoint=%d t=%d", deaths, apIndex < waypoints.Size() ? waypoints[apIndex].args[0] : -1, Level.Time);
            }
            if (deadTimer == 20) Level.MakeScreenShot();   // death screen evidence (HUD, portrait)
            // Like a player on the death screen: press use once to resume from the last save.
            if (deadTimer == 70 && pacifist && deaths == 1)
            {
                p.player.cmd.buttons |= BT_USE;
                Console.Printf("RF_DEV_RESUME_REQUESTED");
            }
            if (deadTimer == 70 && !(pacifist && deaths == 1))
                Console.Printf("RF_DEV_AUTOPILOT_DEAD waypoint=%d", apIndex < waypoints.Size() ? waypoints[apIndex].args[0] : -1);
            return;
        }
        p.player.cmd.forwardmove = 0;
        p.player.cmd.sidemove = 0;
        p.player.cmd.buttons &= ~(BT_ATTACK | BT_USE | BT_RELOAD);
        // A wound means the way is contested, not blocked: the stall clock restarts. A harmless
        // blocker still ends the run as stuck after 20 s.
        if (p.health < apLastHealth) apStuckTimer = 0;
        apLastHealth = p.health;
        if (apDone || waypoints.Size() == 0 || apIndex >= waypoints.Size()) return;
        apTotal++;
        if (apTotal == 35 * 600)
        {
            Console.Printf("RF_DEV_AUTOPILOT_TIMEOUT waypoint=%d", waypoints[apIndex].args[0]);
            apDone = true;
            return;
        }
        Actor wp = waypoints[apIndex];
        Actor foe = FindFoe(p);
        if (apUseCooldown > 0) apUseCooldown--;

        // The pacifist first life never fires: it keeps to the route until an enemy kills it.
        if (foe != null && !(pacifist && deaths == 0))
        {
            if (foe != apFoe)
            {
                apFoe = foe;
                String cls = foe.GetClassName();
                Console.Printf("RF_DEV_FIGHT class=%s tid=%d dist=%.0f hp=%d", cls, foe.tid, p.Distance2D(foe), p.health);
            }
            // Fight: face, aim, semi-auto fire, reload when the FAL runs dry.
            Vector3 aim = foe.Vec3To(p);
            p.angle = p.AngleTo(foe);
            double dz = (foe.pos.z + foe.height * 0.55) - (p.pos.z + p.ViewHeight);
            double dxy = p.Distance2D(foe);
            p.pitch = -atan2(dz, max(dxy, 1));
            Weapon w = FightWeapon(p);
            if (w != null && p.player.ReadyWeapon != w && p.player.PendingWeapon == WP_NOCHANGE)
                p.player.PendingWeapon = w;
            // Fire only when the bullet path really reaches the foe (sight passes over a step edge
            // that a bullet leaving at chest height would hit); otherwise close in, like a player.
            FLineTraceData lt;
            p.LineTrace(p.angle, dxy + 128, p.pitch, 0, p.Height * 0.5 + p.AttackZOffset, 0, 0, lt);
            bool clear = lt.HitType == TRACE_HitActor && lt.HitActor == foe;
            let fal = RFFAL(p.player.ReadyWeapon);
            if (fal != null && fal.Magazine == 0 && !fal.Reloading && fal.ReserveCount() > 0)
                p.player.cmd.buttons |= BT_RELOAD;
            else if (clear && (ticks & 3) == 0 && dxy < 1100) p.player.cmd.buttons |= BT_ATTACK;
            // Keep distance from melee threats while shooting; advance on far or masked foes.
            if (dxy < 160) p.player.cmd.forwardmove = -0x3200;
            else if (!clear || dxy > 420) p.player.cmd.forwardmove = 0x2800;
            if ((ticks % 35) == 0)
                Console.Printf("RF_DEV_FIGHTING foe=%s hp=%d dist=%.0f %s", foe.GetClassName(), foe.health, dxy, AmmoState(p));
            return;
        }

        // Detour for a pickup close to the path; give up on it after 2 s without success.
        if (apItem == null || apItem.Owner != null || apItem.bDestroyed)
        {
            apItem = FindPickup(p);
            apItemTimer = 0;
        }
        if (apItem != null)
        {
            if (++apItemTimer > 70) { apSkip.Push(apItem); apItem = null; }
            else
            {
                Vector2 di = apItem.Pos.XY - p.Pos.XY;
                p.angle = atan2(di.Y, di.X);
                p.pitch = 0;
                p.player.cmd.forwardmove = 0x3200;
                return;
            }
        }

        Vector2 d = wp.Pos.XY - p.Pos.XY;
        double dist = d.Length();
        if (dist < 24)
        {
            int flags = wp.args[1];
            if (wp.args[3] > 0)
            {
                Weapon w = null;
                if (wp.args[3] == 1) w = Weapon(p.FindInventory('RFBrowning'));
                if (wp.args[3] == 2) w = Weapon(p.FindInventory('RFFAL'));
                if (w != null && p.player.ReadyWeapon != w && p.player.PendingWeapon == WP_NOCHANGE) p.player.PendingWeapon = w;
            }
            if (flags & 1)
            {
                p.angle = wp.angle;
                // Exactly one press per waypoint: a second press would close a raise door again.
                if (apTimer == 0)
                {
                    if (DoorAheadOpen(p))
                        Console.Printf("RF_DEV_USE_SKIPPED waypoint=%d door already open", wp.args[0]);
                    else
                    {
                        p.player.cmd.buttons |= BT_USE;
                        apUseCooldown = 120;
                        Console.Printf("RF_DEV_USE waypoint=%d", wp.args[0]);
                        let director = RFDirector(EventHandler.Find('RFDirector'));
                        if (director != null) director.UsePressed(p, true);
                    }
                }
            }
            if (++apTimer >= max(wp.args[2], (flags & 1) ? 40 : 2))
            {
                Console.Printf("RF_DEV_WAYPOINT reached=%d t=%d hp=%d", wp.args[0], Level.Time, p.health);
                if (saveAt > 0 && wp.args[0] == saveAt)
                {
                    Level.MakeAutoSave();
                    Console.Printf("RF_DEV_SAVE_REQUESTED waypoint=%d", wp.args[0]);
                }
                apIndex++;
                apTimer = 0;
                apStuckTimer = 0;
                apBestDist = 1e9;
                if (apIndex >= waypoints.Size()) { apDone = true; Console.Printf("RF_DEV_AUTOPILOT_DONE"); }
            }
            return;
        }
        p.angle = atan2(d.Y, d.X);
        p.pitch = 0;
        p.player.cmd.forwardmove = 0x3200;
        if ((ticks % 35) == 0)
            Console.Printf("RF_DEV_POS t=%d x=%.0f y=%.0f z=%.0f hp=%d wp=%d dist=%.0f %s", Level.Time, p.Pos.X, p.Pos.Y, p.Pos.Z, p.health, wp.args[0], dist, AmmoState(p));
        // Stuck detection: no progress toward the waypoint for a while -> use, jiggle, report.
        if (dist < apBestDist - 1) { apBestDist = dist; apStuckTimer = 0; }
        else
        {
            apStuckTimer++;
            // One use per door cycle (a door takes ~55 tics to open), never a toggle.
            if (apStuckTimer > 35 && apUseCooldown == 0 && !DoorAheadOpen(p)) { p.player.cmd.buttons |= BT_USE; apUseCooldown = 120; }
            if (apStuckTimer > 70) p.player.cmd.sidemove = ((apStuckTimer / 25) & 1) ? 0x2800 : -0x2800;
            if (apStuckTimer == 35 * 6)
            {
                Console.Printf("RF_DEV_STUCK waypoint=%d x=%.0f y=%.0f", wp.args[0], p.Pos.X, p.Pos.Y);
                Level.MakeScreenShot();   // what blocks the route
                let near = ThinkerIterator.Create('RFEnemy');
                RFEnemy en;
                while ((en = RFEnemy(near.Next())) != null)
                    if (en.health > 0 && p.Distance2D(en) < 256)
                        Console.Printf("RF_DEV_NEAR class=%s tid=%d dist=%.0f cue=%d target=%d angle=%.0f frame=%d",
                            en.GetClassName(), en.tid, p.Distance2D(en), en.awaitingCue, en.target == p, en.angle, en.frame);
                // A fight can push the player off the route (behind a counter): walk back to the
                // previous waypoint once, then on along the designed path. A second stall fails.
                if (apBacktrackFor != apIndex && apIndex > 0)
                {
                    apBacktrackFor = apIndex;
                    apIndex--;
                    apBestDist = 1e9;
                    apStuckTimer = 0;
                    Console.Printf("RF_DEV_BACKTRACK waypoint=%d", waypoints[apIndex].args[0]);
                }
            }
            if (apStuckTimer == 35 * 20)
            {
                Console.Printf("RF_DEV_AUTOPILOT_STUCK waypoint=%d x=%.0f y=%.0f", wp.args[0], p.Pos.X, p.Pos.Y);
                apDone = true;
            }
        }
    }
}
