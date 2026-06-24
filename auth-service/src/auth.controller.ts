import { Body, Controller, Get, Post } from '@nestjs/common';
import { IsEmail, IsString, MinLength } from 'class-validator';

class LoginDto {
  @IsEmail()
  email!: string;

  @IsString()
  @MinLength(6)
  password!: string;
}

class OtpRequestDto {
  @IsEmail()
  email!: string;
}

@Controller('auth')
export class AuthController {
  @Post('login')
  login(@Body() body: LoginDto) {
    return {
      accessToken: 'mock.jwt.token',
      user: {
        id: 'user_001',
        email: body.email,
        role: 'Sales Staff'
      }
    };
  }

  @Post('otp/request')
  requestOtp(@Body() body: OtpRequestDto) {
    return {
      status: 'queued',
      message: `OTP requested for ${body.email}`
    };
  }

  @Get('me')
  me() {
    return {
      id: 'user_001',
      email: 'staff@example.com',
      roles: ['Admin', 'Designer', 'Store Manager', 'Sales Staff']
    };
  }
}

