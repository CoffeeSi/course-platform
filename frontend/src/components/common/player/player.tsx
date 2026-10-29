'use client';

import { useEffect, useState, useMemo } from 'react';
import '@videojs/react/video/skin.css';
import { createPlayer, videoFeatures } from '@videojs/react';
import { VideoSkin, Video } from '@videojs/react/video';
import client from '@/shared/api/client';

const Player = createPlayer({ features: videoFeatures });

interface MyPlayerProps {
  videoKey: string;
}

export const VideoPlayer = ({ videoKey }: MyPlayerProps) => {
  const [streamUrl, setStreamUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    const fetchUrl = async () => {
      if (!videoKey) {
        setError('Video path is missing.');
        return;
      }

      setStreamUrl(null);
      setError(null);

      try {
        // customFetch возвращает уже готовые десериализованные данные типа T
        const data = await client.get<{ url: string }>(
          `/api/v1/video/video-url?key=${encodeURIComponent(videoKey)}`
        );

        if (!isCancelled) {
          if (data && data.url) {
            setStreamUrl(data.url);
          } else {
            throw new Error('Invalid response structure from media view');
          }
        }
      } catch (err) {
        if (!isCancelled) {
          console.error("Video stream resolution error:", err);
          setError('Could not load the media stream.');
        }
      }
    };

    fetchUrl();

    return () => {
      isCancelled = true;
    };
  }, [videoKey]);

  const playerKey = useMemo(() => `player-${videoKey}-${streamUrl}`, [videoKey, streamUrl]);

  if (error) return <div className="text-destructive font-medium p-4 border rounded-md bg-destructive/10">{error}</div>;
  if (!streamUrl) return <div className="text-muted-foreground animate-pulse p-4 text-center">Securing storage connection...</div>;

  return (
    <Player.Provider key={playerKey}>
      <VideoSkin>
        <Video
          src={streamUrl}
          playsInline
          suppressHydrationWarning
        />
      </VideoSkin>
    </Player.Provider>
  );
};