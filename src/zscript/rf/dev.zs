// Development harness. Enabled only through the noarchive cvars rf_dev_tour /
// rf_dev_autopilot. Prints machine-readable RF_DEV_* markers to the console/log.
class RFDevHandler : StaticEventHandler
{
    bool tour;
    bool autopilot;
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
        int monsters = 0, items = 0;
        let all = ThinkerIterator.Create('Actor');
        while ((a = Actor(all.Next())) != null)
        {
            if (a.bIsMonster && a.health > 0) monsters++;
            else if (a is 'Inventory' && Inventory(a).Owner == null) items++;
        }
        Console.Printf("RF_DEV_LOADED map=%s save=%d sectors=%d lines=%d monsters=%d items=%d tour=%d waypoints=%d",
            Level.MapName, e.IsSaveGame, Level.Sectors.Size(), Level.Lines.Size(), monsters, items, tourPoints.Size(), waypoints.Size());
    }

    override void WorldUnloaded(WorldEvent e)
    {
        Console.Printf("RF_DEV_UNLOADED map=%s time=%d", Level.MapName, Level.Time);
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

    // Steers the player through RFDevWaypoint markers using ordinary input.
    void DriveAutopilot(PlayerPawn p)
    {
        if (p.player == null || p.health <= 0) return;
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

        if (foe != null)
        {
            // Fight: face, aim, semi-auto fire, reload when the FAL runs dry.
            Vector3 aim = foe.Vec3To(p);
            p.angle = p.AngleTo(foe);
            double dz = (foe.pos.z + foe.height * 0.55) - (p.pos.z + p.ViewHeight);
            double dxy = p.Distance2D(foe);
            p.pitch = -atan2(dz, max(dxy, 1));
            let fal = RFFAL(p.FindInventory('RFFAL'));
            if (fal != null && p.player.ReadyWeapon != fal && p.player.PendingWeapon == WP_NOCHANGE)
                p.player.PendingWeapon = fal;
            if (fal != null && p.player.ReadyWeapon == fal && fal.Magazine == 0 && !fal.Reloading)
                p.player.cmd.buttons |= BT_RELOAD;
            else if ((ticks & 3) == 0) p.player.cmd.buttons |= BT_ATTACK;
            // Keep distance from melee threats while shooting.
            if (dxy < 160) p.player.cmd.forwardmove = -0x3200;
            return;
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
                if (apUseCooldown == 0)
                {
                    p.player.cmd.buttons |= BT_USE;
                    apUseCooldown = 24;
                    Console.Printf("RF_DEV_USE waypoint=%d", wp.args[0]);
                }
            }
            if (++apTimer >= max(wp.args[2], (flags & 1) ? 40 : 2))
            {
                Console.Printf("RF_DEV_WAYPOINT reached=%d t=%d hp=%d", wp.args[0], Level.Time, p.health);
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
            Console.Printf("RF_DEV_POS t=%d x=%.0f y=%.0f z=%.0f hp=%d wp=%d dist=%.0f", Level.Time, p.Pos.X, p.Pos.Y, p.Pos.Z, p.health, wp.args[0], dist);
        // Stuck detection: no progress toward the waypoint for a while -> use, jiggle, report.
        if (dist < apBestDist - 1) { apBestDist = dist; apStuckTimer = 0; }
        else
        {
            apStuckTimer++;
            if (apStuckTimer > 35 && apUseCooldown == 0) { p.player.cmd.buttons |= BT_USE; apUseCooldown = 30; }
            if (apStuckTimer > 70) p.player.cmd.sidemove = ((apStuckTimer / 25) & 1) ? 0x2800 : -0x2800;
            if (apStuckTimer == 35 * 6) Console.Printf("RF_DEV_STUCK waypoint=%d x=%.0f y=%.0f", wp.args[0], p.Pos.X, p.Pos.Y);
        }
    }
}
