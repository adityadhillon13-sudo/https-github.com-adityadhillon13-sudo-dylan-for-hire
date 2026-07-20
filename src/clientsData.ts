export type CandidateRole = 'CNA' | 'LPN' | 'RN';

export interface ClientCenter {
  id: string;
  name: string;
  borough: 'Bronx' | 'Brooklyn' | 'Manhattan' | 'Queens' | 'Staten Island' | 'Long Island';
  address?: string;
  contact?: string;
  email?: string;
  rates: {
    CNA: number;
    LPN: number;
    RN: number;
    RNS?: number;
    HHA?: number;
    [key: string]: number | undefined;
  };
}

export interface Client {
  id: string;
  name: string;
  supportEmail: string;
  supportPhone: string;
  centers: ClientCenter[];
}

export interface CommunicationTemplate {
  id: string;
  name: string;
  category: string;
  content: string;
  description: string;
}

export const COMM_TEMPLATES: CommunicationTemplate[] = [
  {
    id: 'intro',
    name: 'Introduction (First Contact)',
    category: 'Recruiting / Outreach',
    description: 'First-contact outreach to a new candidate. Includes required opt-out language.',
    content: `Hi

Dylan from Blue Line Staffing.

Thank you for applying to our position. How quickly are you looking to start?

Once you confirm, I will send across the basic documents we need to verify and locations for you to choose one. Please specify what nursing license you hold when giving consent to message further.

Should you wish to opt out, please reply STOP or UNSUBSCRIBE.

Thanks

Dylan`
  },
  {
    id: 'med_docs',
    name: 'Medical Documents Checklist',
    category: 'Credentials Intake',
    description: 'Standalone required credential checklist, no rate/center content attached.',
    content: `Do you have the following required documents?

Updated Resume
Nursing License
Two forms of ID- Social security card, passport, driving license, resident card etc
Physical ( less than 12 months old)
MMR titers
Chest XRay and PPD OR Quantiferon ( less than 9 months old)
VARICELLA
Covid Vaccine
BLS/ CPR

If you have these updated, please email them to me at info@bluelinestaffing.com .`
  },
  {
    id: 'rn_rates',
    name: 'RN Rates & Document Checklist',
    category: 'Pitch / Placement',
    description: 'Full document checklist paired with the RN rates & multiple center strategy.',
    content: `Please take the time to digest it and if we get it right the first time, we save time and can prepare your file quickly.

Do you have the following required documents?

Updated Resume
Nursing License
Two forms of ID- Social security card, passport, driving license, resident card etc
Physical ( less than 12 months old)
MMR titers
Chest XRay and PPD OR Quantiferon ( less than 9 months old)
VARICELLA
Covid Vaccine
BLS/ CPR

If you have these updated, please email them to me at info@bluelinestaffing.com . Please try to attach all documents onto one email.

RN rates are listed in the center list.

Please pick a minimum of 3 centers which can work for you - pick as many as possible for you to commute into. Center needs change daily so it is best if we have a multi pronged approach to get placed quickly. Frustrating when we apply to one, they take a week to come back and say this isnt open.

SO, CHOOSE AS MANY AS YOU CAN COMMUTE INTO !!`
  },
  {
    id: 'lpn_rates',
    name: 'LPN Rates & Document Checklist',
    category: 'Pitch / Placement',
    description: 'Full document checklist paired with the LPN rates & multiple center strategy.',
    content: `Please take the time to digest it and if we get it right the first time, we save time and can prepare your file quickly.

Do you have the following required documents?

Updated Resume
Nursing License
Two forms of ID- Social security card, passport, driving license, resident card etc
Physical ( less than 12 months old)
MMR titers
Chest XRay and PPD OR Quantiferon ( less than 9 months old)
VARICELLA
Covid Vaccine
BLS/ CPR

If you have these updated, please email them to me at info@bluelinestaffing.com . Please try to attach all documents onto one email.

LPN rates are listed in the center list.

Please pick a minimum of 3 centers which can work for you - pick as many as possible for you to commute into. Center needs change daily so it is best if we have a multi pronged approach to get placed quickly. Frustrating when we apply to one, they take a week to come back and say this isnt open.

SO, CHOOSE AS MANY AS YOU CAN COMMUTE INTO !!`
  },
  {
    id: 'cna_rates',
    name: 'CNA Rates & Document Checklist',
    category: 'Pitch / Placement',
    description: 'Full document checklist paired with the CNA rates & multiple center strategy.',
    content: `Please take the time to digest it and if we get it right the first time, we save time and can prepare your file quickly.

Do you have the following required documents?

Updated Resume
Nursing License
Two forms of ID- Social security card, passport, driving license, resident card etc
Physical ( less than 12 months old)
MMR titers
Chest XRay and PPD OR Quantiferon ( less than 9 months old)
VARICELLA
Covid Vaccine
BLS/ CPR

If you have these updated, please email them to me at info@bluelinestaffing.com . Please try to attach all documents onto one email.

CNA rates are listed in the center list.

Please pick a minimum of 3 centers which can work for you - pick as many as possible for you to commute into. Center needs change daily so it is best if we have a multi pronged approach to get placed quickly. Frustrating when we apply to one, they take a week to come back and say this isnt open.

SO, CHOOSE AS MANY AS YOU CAN COMMUTE INTO !!`
  },
  {
    id: 'multi_centers',
    name: 'Multi-Center Strategy Pitch',
    category: 'Candidate Guidance',
    description: 'Explanation of why applying to multiple facilities simultaneously increases placement speed.',
    content: `I encourage applying to as many centers as you can commute into. Applying 1 by 1 is both a waste of time (due to delays in responses and email exchange with that center) and can get incredibly frustrating in the waiting only to realise there is no opening. By doing it my way, whoever has an opening and responds to us gets the interview and this speeds up the entire placement process- does that make sense?`
  },
  {
    id: 'add_on_info',
    name: 'Add-On Shift & Mode Inquiry',
    category: 'Recruiting / Intake',
    description: 'Asks candidate for their resume, shift preferences, and full-time vs part-time status.',
    content: `IMPORTANT- When responding include a copy of your most recent resume, which shift we want to take on- am/ pm or night and full or part time work- and if part time, how many shifts per week. pick a minimum of 3 centers which can work for you - pick as many as possible for you to commute into. Center needs change daily so it is best if we have a multi pronged approach to get placed quickly. Frustrating when we apply to one, they take a week to come back and say this isnt open.

SO, CHOOSE AS MANY AS YOU CAN COMMUTE INTO !!`
  },
  {
    id: 'shift_ft_pt',
    name: 'Shift & FT/PT Preference Check',
    category: 'Candidate Guidance',
    description: 'Inquiry message when shift preferences or scheduling mode is missing from chats.',
    content: `I scrolled through our chat and don't see anything about-

1. Shift preference- AM/PM/Night ( can choose more than 1 to increase chances if your schedule allows it- you will open up new vacancies by doing so (will work only 1 of those shifts and not fluctuate)

2. Full time/ Part time/Per Diem`
  },
  {
    id: 'add_more_centers',
    name: 'Add More Centers Follow-up',
    category: 'Urgent Prodding',
    description: 'Follow-up nudge to add more centers if initial selection responses are delayed.',
    content: `Good morning. I'm not the most patient person- which is horrible in my personal life, but works super for work. I have just finished sending the 3rd reminder to the centers you chose. Do you want to consider adding more centers so we can keep pushing aggressively to save time? In no way am I saying we are stuck- just want to get you set up asap!! Make sense?`
  },
  {
    id: 'sending_info',
    name: 'Sending Info - Digest & Action',
    category: 'Candidate Guidance',
    description: 'Polite prompt urging the candidate to review and process a heavy packet of information.',
    content: `Sending you a bunch of info- please digest and action accordingly and let's get you into a center asap..sound good? If you have any unanswered questions or concerns at any time, please dont hesitate.`
  },
  {
    id: 'pleasure_to_serve',
    name: 'Pleasure to Serve / One Email',
    category: 'Candidate Guidance',
    description: 'Closing message reinforcing the process and requesting documents in a single email thread.',
    content: `If you need anything, please don't hesitate to reach out. I look forward to helping you get placed asap- if we work together it can be as early as next week if we follow the process mapped above. Try sending the medical docs in one email pls.`
  },
  {
    id: 'cant_confirm_shift',
    name: "Can't Confirm Shift Yet",
    category: 'Candidate Guidance',
    description: 'Response handling candidates asking for guaranteed shifts before files are fully audited.',
    content: `Centers work with multiple agencies for recruitment. And because of this staffing needs at centers change daily, if not hourly. We can check availability once our file is ready but generally speaking, finding a match for our file isn't a real issue.`
  },
  {
    id: 'borough_select',
    name: 'Borough Request for Center List',
    category: 'Recruiting / Outreach',
    description: 'Asks the candidate which borough of centers they would prefer to review.',
    content: `Which borough center list can I share for you to choose sites? Please either consider your place of residence or ease of commuting for this and i will share whatever borough to can access for work.`
  }
];

export const CLIENTS_REGISTRY: Client[] = [
  {
    id: 'blueline',
    name: 'BlueLine Staffing',
    supportEmail: 'info@bluelinestaffing.com',
    supportPhone: '(551) 250-6678',
    centers: [
      {
        id: 'bronx-gardens',
        name: 'Bronx Gardens (Citadel Group)',
        borough: 'Bronx',
        contact: 'Diane Murillo',
        email: 'DianeM@citadelcarecenters.com',
        rates: { CNA: 30, LPN: 53.75, RN: 63, RNS: 65 }
      },
      {
        id: 'plaza-rehab',
        name: 'Plaza Rehabilitation (Citadel Group)',
        borough: 'Bronx',
        contact: 'Maurice F',
        email: 'MauriceF@citadelcarecenters.com',
        rates: { CNA: 30, LPN: 53.75, RN: 63, RNS: 65 }
      },
      {
        id: 'hudson-pointe',
        name: 'Hudson Pointe (Citadel Group)',
        borough: 'Bronx',
        address: '3220 Henry Hudson Pkwy, Bronx, NY 10463',
        contact: 'Marquis B',
        email: 'MarquisB@citadelcarecenters.com',
        rates: { CNA: 30, LPN: 53.75, RN: 63, RNS: 65 }
      },
      {
        id: 'riverdale-nursing',
        name: 'Riverdale Nursing (Citadel Group)',
        borough: 'Bronx',
        address: '641 W 230th St, Bronx, NY 10463',
        contact: 'Maurice F',
        email: 'MauriceF@citadelcarecenters.com',
        rates: { CNA: 30, LPN: 53.75, RN: 63, RNS: 65 }
      },
      {
        id: 'green-hill',
        name: 'Green Hill Senior Living',
        borough: 'Bronx',
        contact: 'M. Moreno',
        email: 'MMoreno@green-hill.com',
        rates: { CNA: 30, LPN: 53.75, RN: 63, RNS: 65 }
      },
      {
        id: 'bronx-park',
        name: 'Bronx Park Rehabilitation Center',
        borough: 'Bronx',
        address: '3845 Carpenter Ave, Bronx, NY 10467',
        contact: 'Alexander Goldberger (Admin)',
        email: 'AGoldberger@bronxparkcenter.com',
        rates: { CNA: 31.95, LPN: 59, RN: 75 }
      },
      {
        id: 'split-rock',
        name: 'Split Rock Center',
        borough: 'Bronx',
        address: '3525 Baychester Ave, Bronx, NY 10466',
        contact: 'Carmen Alvarez',
        email: 'CAlvarez@splitrockrehab.com',
        rates: { CNA: 31, LPN: 57, RN: 70, RNS: 75 }
      },
      {
        id: 'rebekah-care',
        name: 'Rebekah Care Center',
        borough: 'Bronx',
        address: '1072 Havemeyer Ave, Bronx, NY 10462',
        contact: 'Shellian Cormack',
        email: 'scormack@rebekahrehab.org',
        rates: { CNA: 32.75, LPN: 57.75, RN: 68, RNS: 75, HHA: 26.50 }
      },
      {
        id: 'workmens-circle',
        name: 'Workmens Circle Multicare Center',
        borough: 'Bronx',
        address: '3155 Grace Ave, Bronx, NY 10469',
        contact: 'Roochelly Mercedes',
        email: 'rmercedes@wcmcc.org',
        rates: { CNA: 29.50, LPN: 49, RN: 62, RNS: 69 }
      },
      {
        id: 'morningside-nursing',
        name: 'Morningside Nursing Home',
        borough: 'Bronx',
        address: '1000 Pelham Pkwy S, Bronx, NY 10461',
        contact: 'Aida Rodriguez',
        email: 'AidaRodriguez@morningsidenrc.com',
        rates: { CNA: 29.50, LPN: 49, RN: 62, RNS: 69 }
      },
      {
        id: 'fordham-nursing',
        name: 'Fordham Nursing and Rehabilitation',
        borough: 'Bronx',
        address: '2678 Kingsbridge Terrace, Bronx, NY 10463',
        contact: 'K. Williams',
        email: 'KWilliams@fordhamnrc.com',
        rates: { CNA: 29.50, LPN: 49, RN: 62, RNS: 69 }
      },
      {
        id: 'fort-tryon',
        name: 'Fort Tryon Rehab',
        borough: 'Manhattan',
        contact: 'Angelica Espinal',
        email: 'angelica@forttryonrehab.com',
        rates: { CNA: 31, LPN: 57, RN: 70, RNS: 75 }
      },
      {
        id: 'riverside-rehab',
        name: 'Riverside Rehabilitation',
        borough: 'Bronx',
        contact: 'N. Sathi',
        email: 'nsathi@theriversiderehab.com',
        rates: { CNA: 30, LPN: 56, RN: 65 }
      },
      {
        id: 'brooklyn-queens-nh',
        name: 'Brooklyn Queens Nursing Home',
        borough: 'Brooklyn',
        address: '2749 Linden Blvd, Brooklyn, NY 11208',
        contact: 'Administrator',
        email: 'administrator@bqrehab.com',
        rates: { CNA: 29, LPN: 55.75, RN: 69.50, RNS: 73.50 }
      },
      {
        id: 'brooklyn-gardens',
        name: 'Brooklyn Gardens',
        borough: 'Brooklyn',
        address: '835 Herkimer St, Brooklyn, NY 11233',
        contact: 'A. Stamps',
        email: 'AStamps@brooklyngardens.com',
        rates: { CNA: 30.25, LPN: 57.75, RN: 75, RNS: 83 }
      },
      {
        id: 'caton-park',
        name: 'Caton Park Center',
        borough: 'Brooklyn',
        address: '1312 Caton Ave, Brooklyn, NY',
        contact: 'C. Footman',
        email: 'CFootman@catonpark.com',
        rates: { CNA: 30, LPN: 55.75, RN: 75.50 }
      },
      {
        id: 'downtown-brooklyn-nursing',
        name: 'Downtown Brooklyn Nursing (DBNRC)',
        borough: 'Brooklyn',
        address: '520 Prospect Place, Brooklyn, NY 11238',
        contact: 'Maksim Meyer',
        email: 'mmeyer@dbnrc.com',
        rates: { CNA: 29.50, LPN: 49, RN: 62, RNS: 69 }
      },
      {
        id: 'palm-gardens',
        name: 'Palm Gardens Rehab (Palm Gardens CNR)',
        borough: 'Brooklyn',
        address: '615 Avenue C, Brooklyn, NY 11218',
        contact: 'Amy Woo',
        email: 'AWoo@pgcnh.com',
        rates: { CNA: 30.75, LPN: 56.75, RN: 73.50, RNS: 80.50 }
      },
      {
        id: 'norwegian-christian',
        name: 'Norwegian Christian Home & Health Center',
        borough: 'Brooklyn',
        address: '1250 67th St, Brooklyn, NY 11219',
        contact: 'J. Morales',
        email: 'jmorales@nchhc.org',
        rates: { CNA: 31.50, LPN: 57, RN: 75 }
      },
      {
        id: 'verazanno-nh',
        name: 'Verazanno Nursing Home',
        borough: 'Queens',
        contact: 'W. Peralta',
        email: 'WPeralta@vnhsi.com',
        rates: { CNA: 31.75, LPN: 56.75, RN: 73, RNS: 77 }
      },
      {
        id: 'park-nursing-home',
        name: 'Park Nursing Home',
        borough: 'Queens',
        address: '128 Beach 115th St, Rockaway Park, NY',
        contact: 'I. Berger',
        email: 'IBerger@parknh.com',
        rates: { CNA: 32.75, LPN: 55.75, RN: 68, RNS: 75 }
      },
      {
        id: 'rockaway-care',
        name: 'Rockaway Care Center',
        borough: 'Queens',
        address: '353 Beach 48th St, Far Rockaway, NY',
        contact: 'F. Wilson',
        email: 'FWilson@rockawaycc.com',
        rates: { CNA: 31.25, LPN: 55.75, RN: 75.50 }
      },
      {
        id: 'queens-nassau',
        name: 'Queens Nassau Nursing',
        borough: 'Queens',
        address: '520 Beach 19th St, Far Rockaway, NY',
        contact: 'Y. Williams',
        email: 'ywilliams@queensnassaurehab.com',
        rates: { CNA: 31, LPN: 46, RN: 55 }
      },
      {
        id: 'forest-view-center',
        name: 'Forest View Center',
        borough: 'Queens',
        address: '71-20 110th St, Forest Hills, NY 11375',
        contact: 'Debbie Umrao-Paray',
        email: 'dp@fvrehab.com',
        rates: { CNA: 31.75, LPN: 55, RN: 68, RNS: 72 }
      },
      {
        id: 'cliffside-center',
        name: 'Cliffside Center',
        borough: 'Queens',
        address: '119-19 Graham Ct, Queens, NY 11354',
        contact: 'Debbie Umrao-Paray',
        email: 'dp@fvrehab.com',
        rates: { CNA: 31.75, LPN: 55, RN: 68, RNS: 72 }
      },
      {
        id: 'woodcrest-center',
        name: 'Woodcrest Center',
        borough: 'Queens',
        address: '11909 26th Ave, Flushing, NY 11354',
        contact: 'Debbie Umrao-Paray',
        email: 'dp@fvrehab.com',
        rates: { CNA: 31.75, LPN: 55, RN: 68, RNS: 72 }
      },
      {
        id: 'new-franklin',
        name: 'New Franklin Center',
        borough: 'Queens',
        address: '142-27 Franklin Ave, Queens, NY 11355',
        contact: 'Claribel Pacheco',
        email: 'CPacheco@franklinnh.net',
        rates: { CNA: 31, LPN: 57, RN: 70, RNS: 75 }
      },
      {
        id: 'midway-nursing',
        name: 'Midway Nursing Home',
        borough: 'Queens',
        address: '6995 Queens Midtown Expy, Maspeth, NY 11378',
        contact: 'Cassandra',
        email: 'hr@midwaynh.com',
        rates: { CNA: 29, LPN: 55.75, RN: 69.50, RNS: 73.50 }
      },
      {
        id: 'beach-terrace',
        name: 'Beach Terrace Care Center',
        borough: 'Queens',
        address: '640 W Broadway, Long Beach, NY 11561',
        contact: 'P. Jean Baptiste',
        email: 'pjeanbaptiste@beach-terrace.com',
        rates: { CNA: 32.75, LPN: 57, RN: 75 }
      },
      {
        id: 'hempstead-park',
        name: 'Hempstead Park Nursing Home',
        borough: 'Long Island',
        contact: 'S. Hunte',
        email: 'SHunte@hempsteadparknh.com',
        rates: { CNA: 30.25, LPN: 57.75, RN: 75 }
      }
    ]
  },
  {
    id: 'apex-care',
    name: 'Apex Care Staffing',
    supportEmail: 'contact@apexcare.com',
    supportPhone: '(212) 555-0149',
    centers: [
      {
        id: 'apex-manhattan',
        name: 'Manhattan Rehabilitation Center',
        borough: 'Manhattan',
        contact: 'Sarah Jenkins',
        email: 'sjenkins@apexmanhattan.com',
        rates: { CNA: 32, LPN: 58, RN: 78 }
      },
      {
        id: 'apex-brooklyn',
        name: 'Apex Brooklyn Senior Living',
        borough: 'Brooklyn',
        contact: 'James Carter',
        email: 'jcarter@apexbrooklyn.com',
        rates: { CNA: 31, LPN: 56, RN: 74 }
      }
    ]
  },
  {
    id: 'metro-nursing',
    name: 'Metro Nursing Services',
    supportEmail: 'admin@metronursing.com',
    supportPhone: '(718) 555-0182',
    centers: [
      {
        id: 'metro-queens',
        name: 'Metro Queens Care Facility',
        borough: 'Queens',
        contact: 'Linda Zhao',
        email: 'lzhao@metronursing.com',
        rates: { CNA: 28.50, LPN: 52, RN: 66 }
      },
      {
        id: 'metro-staten',
        name: 'Staten Island Care Complex',
        borough: 'Staten Island',
        contact: 'Robert Vance',
        email: 'rvance@metronursing.com',
        rates: { CNA: 30, LPN: 54, RN: 72 }
      }
    ]
  }
];
