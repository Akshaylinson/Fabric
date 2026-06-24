import { Module } from '@nestjs/common';
import { HealthController } from './health.controller';
import { ProxyController } from './proxy.controller';

@Module({
  controllers: [HealthController, ProxyController]
})
export class AppModule {}

