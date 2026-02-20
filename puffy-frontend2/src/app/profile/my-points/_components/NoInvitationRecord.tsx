"use client";

export default function NoInvitationRecord() {
  return (
    <div className="w-full h-80 bg-transparent rounded-xl border border-[#E2E2E2] flex flex-col items-center justify-center gap-4">
      <div className="opacity-30">
        <svg
          width="46"
          height="46"
          viewBox="0 0 46 46"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M15 8H31C33.7614 8 36 10.2386 36 13V29.9238C35.9999 30.5885 35.7793 31.2315 35.377 31.7539L35.1934 31.9707L30.4551 37.0469C29.8877 37.6548 29.0933 38 28.2617 38H15C12.2386 38 10 35.7614 10 33V13C10 10.2386 12.2386 8 15 8Z"
            fill="#F6F6F6"
            stroke="black"
            strokeWidth="2"
          />
          <path
            d="M17 16L29 16"
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M17 22L24 22"
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M35 30H31C29.8954 30 29 30.8954 29 32V37"
            stroke="black"
            strokeWidth="2"
          />
        </svg>
      </div>

      <div className="text-black/90 font-normal" style={{ fontSize: 14 }}>
        No invitation record
      </div>
    </div>
  );
}
