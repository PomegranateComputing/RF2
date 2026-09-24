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
        tour = CVar.GetCVar('rf_dev_tour').GetBool();
        autopilot = CVar.GetCVar('rf_dev_autopilot').GetBool();
        doortest = CVar.GetCVar('rf_dev_doortest').GetBool();
        weaponShots = CVar.GetCVar('rf_dev_weapons').GetBool();
        logging = tour || autopilot || doortest || weaponShots || CVar.GetCVar('rf_dev_log').GetBool();
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
        if (p.player == null) return;
        p.player.cheats |= CF_GODMODE;
        p.player.cmd.forwardmove = 0;
        p.player.cmd.sidemove = 0;
        p.player.cmd.buttons &= ~(BT_ATTACK | BT_USE | BT_RELOAD);
        if (ticks == 10)
        {
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
        if (ticks == 45) Level.MakeScreenShot();
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
        if (ticks == 111 || ticks == 113) Level.MakeScreenShot();        // FIRE + flash, RECOIL
        if (ticks == 150) fal.Magazine = 0;
        if (ticks == 152) p.player.cmd.buttons |= BT_RELOAD;
        if (ticks > 152 && ticks <= 212 && (ticks - 152) % 8 == 0) Level.MakeScreenShot();   // reload poses
        if (ticks == 230) Level.MakeScreenShot();                        // ready again
        if (ticks == 240) Console.Printf("RF_DEV_WEAPONS_DONE mag=%d reserve=%d", fal.Magazine, fal.ReserveCount());
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
            }
            if (apStuckTimer == 35 * 20)
            {
                Console.Printf("RF_DEV_AUTOPILOT_STUCK waypoint=%d x=%.0f y=%.0f", wp.args[0], p.Pos.X, p.Pos.Y);
                apDone = true;
            }
        }
    }
}
