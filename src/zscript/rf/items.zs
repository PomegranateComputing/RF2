// Ammunition, health and keys used by RF01.

class RFPistolAmmo : Ammo
{
    Default
    {
        Inventory.MaxAmount 96;
        Inventory.Amount 12;
        Ammo.BackpackAmount 24;
        Ammo.BackpackMaxAmount 192;
        Inventory.PickupMessage "$RF_AMMO_9MM";
        Inventory.PickupSound "rf/item/pickup";
        Inventory.Icon "RF9MA0";
        Scale 0.45;
    }
    States
    {
    Spawn:
        RF9M A -1;
        Stop;
    }
}

class RFRifleAmmo : Ammo
{
    Default
    {
        Inventory.MaxAmount 160;
        Inventory.Amount 20;
        Ammo.BackpackAmount 40;
        Ammo.BackpackMaxAmount 320;
        Inventory.PickupMessage "$RF_AMMO_762";
        Inventory.PickupSound "rf/item/pickup";
        Inventory.Icon "RFRMA0";
        Scale 0.45;
    }
    States
    {
    Spawn:
        RFRM A -1;
        Stop;
    }
}

class RFFieldDressing : Health
{
    Default
    {
        Inventory.Amount 25;
        Inventory.MaxAmount 100;
        Inventory.PickupMessage "$RF_ITEM_DRESSING";
        Inventory.PickupSound "rf/item/pickup";
        Scale 0.45;
    }
    States
    {
    Spawn:
        RFMD A -1;
        Stop;
    }
}

// Keys are contextual objects, not colored cards. Lock numbers live in LOCKDEFS.
class RFGrilleKey : Key
{
    Default
    {
        Inventory.PickupMessage "$RF_PICKUP_GRILLEKEY";
        Inventory.PickupSound "rf/item/pickup";
        Inventory.Icon "RFKYA0";
        Tag "$RF_KEY_GRILLE";
        Scale 0.5;
    }
    States
    {
    Spawn:
        RFKY A -1;
        Stop;
    }
}

class RFPasseKey : Key
{
    Default
    {
        Inventory.PickupMessage "$RF_PICKUP_PASSE";
        Inventory.PickupSound "rf/item/pickup";
        Inventory.Icon "RFKYB0";
        Tag "$RF_KEY_PASSE";
        Scale 0.5;
    }
    States
    {
    Spawn:
        RFKY B -1;
        Stop;
    }
}
